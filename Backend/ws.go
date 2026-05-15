package main

import (
	"encoding/json"
	"log"
	"net/http"
	"sync"
	"time"

	"github.com/gorilla/websocket"
)

var upgrader = websocket.Upgrader{
	CheckOrigin: func(r *http.Request) bool {
		return true
	},
	ReadBufferSize:  1024,
	WriteBufferSize: 1024,
}

type Client struct {
	userID int
	conn   *websocket.Conn
	hub    *Hub
	send   chan []byte
}

type Hub struct {
	mu         sync.RWMutex
	clients    map[int]map[*Client]bool
	jwtManager *JWTManager
	db         *DB
	encrypt    *Encrypt
}

func NewHub(jm *JWTManager, db *DB, enc *Encrypt) *Hub {
	return &Hub{
		clients:    make(map[int]map[*Client]bool),
		jwtManager: jm,
		db:         db,
		encrypt:    enc,
	}
}

func (h *Hub) HandleWS(w http.ResponseWriter, r *http.Request) {
	userID := h.GetUserIDFromCookie(r)

	conn, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		log.Printf("WS upgrade error: %v", err)
		return
	}

	client := &Client{
		userID: userID,
		conn:   conn,
		hub:    h,
		send:   make(chan []byte, 256),
	}

	if userID > 0 {
		h.mu.Lock()
		if h.clients[userID] == nil {
			h.clients[userID] = make(map[*Client]bool)
		}
		h.clients[userID][client] = true
		log.Printf("User %d connected via WS (cookie auth)", userID)
		h.mu.Unlock()
	}

	conn.SetCloseHandler(func(code int, text string) error {
		h.unregister(client)
		return nil
	})

	go client.writePump()
	go client.readPump()
}

func (h *Hub) unregister(client *Client) {
	h.mu.Lock()
	defer h.mu.Unlock()

	if client.userID > 0 {
		if clients, ok := h.clients[client.userID]; ok {
			delete(clients, client)
			if len(clients) == 0 {
				delete(h.clients, client.userID)
			}
			log.Printf("User %d disconnected from WS", client.userID)
		}
	}
}

func (h *Hub) sendToUser(userID int, msg []byte) {
	h.mu.RLock()
	defer h.mu.RUnlock()
	if clients, ok := h.clients[userID]; ok {
		for client := range clients {
			select {
			case client.send <- msg:
			default:
			}
		}
	}
}

func (c *Client) writePump() {
	ticker := time.NewTicker(30 * time.Second)
	defer func() {
		ticker.Stop()
		c.conn.Close()
	}()

	for {
		select {
		case message, ok := <-c.send:
			if !ok {
				c.conn.WriteMessage(websocket.CloseMessage, []byte{})
				return
			}
			c.conn.SetWriteDeadline(time.Now().Add(10 * time.Second))
			if err := c.conn.WriteMessage(websocket.TextMessage, message); err != nil {
				return
			}
		case <-ticker.C:
			c.conn.SetWriteDeadline(time.Now().Add(10 * time.Second))
			if err := c.conn.WriteMessage(websocket.PingMessage, nil); err != nil {
				return
			}
		}
	}
}

func (c *Client) readPump() {
	defer func() {
		c.hub.unregister(c)
		c.conn.Close()
	}()

	c.conn.SetReadLimit(65536)
	c.conn.SetReadDeadline(time.Now().Add(60 * time.Second))
	c.conn.SetPongHandler(func(string) error {
		c.conn.SetReadDeadline(time.Now().Add(60 * time.Second))
		return nil
	})

	for {
		_, message, err := c.conn.ReadMessage()
		if err != nil {
			break
		}

		var wsMsg WsMessage
		if err := json.Unmarshal(message, &wsMsg); err != nil {
			continue
		}

		c.handleMessage(wsMsg)
	}
}

func (c *Client) handleMessage(msg WsMessage) {
	switch msg.Type {
	case "join":
		c.handleJoin()
	case "send_message":
		c.handleSendMessage(msg)
	case "read_message":
		c.handleReadMessage(msg)
	case "del_message":
		c.handleDelMessage(msg)
	}
}

func (c *Client) handleJoin() {
	if c.userID > 0 {
		c.hub.mu.Lock()
		if c.hub.clients[c.userID] == nil {
			c.hub.clients[c.userID] = make(map[*Client]bool)
		}
		c.hub.clients[c.userID][c] = true
		c.hub.mu.Unlock()
		log.Printf("User %d join confirmed", c.userID)
	}
}

func (c *Client) handleSendMessage(msg WsMessage) {
	fromID := c.userID
	if fromID <= 0 {
		c.sendJSON(WsOutgoing{Type: "ws_error", Error: "Not authorized"})
		return
	}

	text := msg.Text
	if text == "" {
		c.sendJSON(WsOutgoing{Type: "ws_error", Error: "Empty message", TempID: msg.TempID})
		return
	}

	if msg.ChatID > 0 {
		c.sendToChat(fromID, msg.ChatID, text, msg.TempID)
	} else if msg.ToID > 0 {
		c.sendPrivateMessage(fromID, msg.ToID, text, msg.TempID)
	} else {
		c.sendJSON(WsOutgoing{Type: "ws_error", Error: "None chat_id or to_id", TempID: msg.TempID})
	}
}

func (c *Client) sendToChat(fromID, chatID int, text string, tempID int64) {
	check, err := c.hub.db.Query("SELECT 1 FROM chat_participants WHERE chat_id=? AND user_id=?", chatID, fromID)
	if err != nil || len(check) == 0 {
		c.sendJSON(WsOutgoing{Type: "ws_error", Error: "Client not found in chat", TempID: tempID})
		return
	}

	participants, err := c.hub.db.Query("SELECT user_id FROM chat_participants WHERE chat_id=?", chatID)
	if err != nil {
		c.sendJSON(WsOutgoing{Type: "ws_error", Error: "Server error", TempID: tempID})
		return
	}

	if len(participants) <= 1 {
		c.sendJSON(WsOutgoing{Type: "ws_error", Error: "Cannot send message to yourself", TempID: tempID})
		return
	}

	encrypted, err := c.hub.encrypt.EncryptMessage(text)
	if err != nil {
		c.sendJSON(WsOutgoing{Type: "ws_error", Error: "Encryption error", TempID: tempID})
		return
	}

	msgID, err := c.hub.db.Exec(
		"INSERT INTO chat_message (chat_id, from_id, text) VALUES (?, ?, ?)",
		chatID, fromID, encrypted,
	)
	if err != nil {
		c.sendJSON(WsOutgoing{Type: "ws_error", Error: "Failed to save", TempID: tempID})
		return
	}

	now := time.Now().Format("2006-01-02T15:04:05")

	outMsg := WsOutgoing{
		Type:   "ws_message",
		ID:     msgID,
		FromID: fromID,
		Text:   text,
		Time:   now,
		ChatID: chatID,
	}

	for _, p := range participants {
		uid := toInt(p["user_id"])
		if uid == fromID {
			continue
		}
		c.hub.sendToUser(uid, mustJSON(outMsg))
	}

	c.sendJSON(WsOutgoing{
		Type:      "ws_log",
		Success:   true,
		TempID:    tempID,
		MessageID: msgID,
		ChatID:    chatID,
	})
}

func (c *Client) sendPrivateMessage(fromID, toID int, text string, tempID int64) {
	if fromID == toID {
		c.sendJSON(WsOutgoing{Type: "ws_error", Error: "Cannot send message to yourself", TempID: tempID})
		return
	}

	chatRows, err := c.hub.db.Query(`
		SELECT rq1.chat_id
		FROM chat_participants rq1
		INNER JOIN chat_participants rq2 ON rq1.chat_id = rq2.chat_id
		WHERE rq1.user_id = ? AND rq2.user_id = ? AND rq1.user_id != rq2.user_id
		LIMIT 1
	`, fromID, toID)

	var chatID int64
	if err == nil && len(chatRows) > 0 {
		chatID = int64(toInt(chatRows[0]["chat_id"]))
	} else {
		newChatID, err := c.hub.db.Exec("INSERT INTO chats (type) VALUES (0)")
		if err != nil {
			c.sendJSON(WsOutgoing{Type: "ws_error", Error: "Failed to create chat", TempID: tempID})
			return
		}
		chatID = newChatID
		c.hub.db.Exec("INSERT INTO chat_participants (chat_id, user_id) VALUES (?, ?)", chatID, fromID)
		c.hub.db.Exec("INSERT INTO chat_participants (chat_id, user_id) VALUES (?, ?)", chatID, toID)
	}

	encrypted, err := c.hub.encrypt.EncryptMessage(text)
	if err != nil {
		c.sendJSON(WsOutgoing{Type: "ws_error", Error: "Encryption error", TempID: tempID})
		return
	}

	msgID, err := c.hub.db.Exec(
		"INSERT INTO chat_message (chat_id, from_id, text) VALUES (?, ?, ?)",
		chatID, fromID, encrypted,
	)
	if err != nil {
		c.sendJSON(WsOutgoing{Type: "ws_error", Error: "Failed to save", TempID: tempID})
		return
	}

	now := time.Now().Format("2006-01-02T15:04:05")

	outMsg := WsOutgoing{
		Type:   "ws_message",
		ID:     msgID,
		FromID: fromID,
		Text:   text,
		Time:   now,
		ChatID: chatID,
	}

	c.hub.sendToUser(toID, mustJSON(outMsg))

	c.sendJSON(WsOutgoing{
		Type:      "ws_log",
		Success:   true,
		TempID:    tempID,
		MessageID: msgID,
		ChatID:    chatID,
	})
}

func (c *Client) handleReadMessage(msg WsMessage) {
	userID := c.userID
	if userID <= 0 {
		c.sendJSON(WsOutgoing{Type: "ws_read_error", Error: "Not authorized"})
		return
	}

	chatID := msg.ChatID
	if chatID <= 0 {
		c.sendJSON(WsOutgoing{Type: "ws_read_error", Error: "Not found chat_id"})
		return
	}

	count, err := c.hub.db.ExecAffected(
		"UPDATE chat_message SET is_read=1 WHERE chat_id=? AND from_id!=? AND is_read=0",
		chatID, userID,
	)
	if err != nil {
		c.sendJSON(WsOutgoing{Type: "ws_read_error", Error: "Server error"})
		return
	}

	participants, err := c.hub.db.Query(
		"SELECT user_id FROM chat_participants WHERE chat_id=? AND user_id!=?",
		chatID, userID,
	)
	if err == nil {
		readMsg := WsOutgoing{
			Type:   "ws_chat_read",
			ChatID: chatID,
			Count:  int(count),
			UserID: userID,
		}
		for _, p := range participants {
			uid := toInt(p["user_id"])
			c.hub.sendToUser(uid, mustJSON(readMsg))
		}
	}
}

func (c *Client) handleDelMessage(msg WsMessage) {
	userID := c.userID
	if userID <= 0 {
		c.sendJSON(WsOutgoing{Type: "ws_del_error", Error: "Not authorized"})
		return
	}

	messageID := msg.MessageID
	if messageID <= 0 {
		c.sendJSON(WsOutgoing{Type: "ws_del_error", Error: "Not message id"})
		return
	}

	rows, err := c.hub.db.Query(
		"SELECT chat_id FROM chat_message WHERE from_id=? AND id=?",
		userID, messageID,
	)
	if err != nil || len(rows) == 0 {
		c.sendJSON(WsOutgoing{Type: "ws_del_error", Error: "Message not found"})
		return
	}

	chatID := toInt(rows[0]["chat_id"])

	_, err = c.hub.db.Exec("DELETE FROM chat_message WHERE id=? AND from_id=?", messageID, userID)
	if err != nil {
		c.sendJSON(WsOutgoing{Type: "ws_del_error", Error: "Delete failed"})
		return
	}

	participants, err := c.hub.db.Query(
		"SELECT user_id FROM chat_participants WHERE chat_id=?", chatID,
	)
	if err == nil {
		delMsg := WsOutgoing{
			Type:      "ws_del_message",
			MessageID: messageID,
			ChatID:    chatID,
		}
		for _, p := range participants {
			uid := toInt(p["user_id"])
			c.hub.sendToUser(uid, mustJSON(delMsg))
		}
	}

	c.sendJSON(WsOutgoing{
		Type:      "ws_del_log",
		Success:   true,
		MessageID: messageID,
	})
}

func (c *Client) sendJSON(data interface{}) {
	msg, err := json.Marshal(data)
	if err != nil {
		return
	}
	select {
	case c.send <- msg:
	default:
	}
}

func mustJSON(data interface{}) []byte {
	msg, _ := json.Marshal(data)
	return msg
}

func (h *Hub) GetUserIDFromCookie(r *http.Request) int {
	cookie, err := r.Cookie("token")
	if err != nil {
		return 0
	}
	userID, err := h.jwtManager.ParseToken(cookie.Value)
	if err != nil {
		return 0
	}
	return userID
}

package main

import (
	"sort"
	"strings"
	"time"

	"github.com/gin-gonic/gin"
)

func (h *Handlers) GetChatInfo(c *gin.Context) {
	clientID, _ := c.Get("client_id")

	var req ChatInfoRequest
	if err := c.ShouldBindJSON(&req); err != nil || req.ChatID <= 0 {
		c.JSON(403, gin.H{"Info": "Forbidden"})
		return
	}

	check, _ := h.db.Query("SELECT 1 FROM chat_participants WHERE chat_id=? AND user_id=?", req.ChatID, clientID)
	if len(check) == 0 {
		c.JSON(400, gin.H{"Info": "Access not found"})
		return
	}

	chats, _ := h.db.Query("SELECT type, name FROM chats WHERE id=?", req.ChatID)
	if len(chats) == 0 {
		c.JSON(400, gin.H{"Info": "Chat not found"})
		return
	}

	chatType := toInt(chats[0]["type"])
	chatName := toString(chats[0]["name"])
	otherUserID := 0

	if chatType == 0 {
		others, _ := h.db.Query("SELECT user_id FROM chat_participants WHERE chat_id=? AND user_id!=? LIMIT 1", req.ChatID, clientID)
		if len(others) > 0 {
			otherUserID = toInt(others[0]["user_id"])
			userData, _ := h.db.Query("SELECT username, name FROM accounts WHERE id=?", otherUserID)
			if len(userData) > 0 {
				if name, ok := userData[0]["name"].(string); ok && name != "" {
					dec, err := decryptMeta(name)
					if err == nil {
						chatName = dec
					}
				} else if uname, ok := userData[0]["username"].(string); ok {
					dec, err := decryptMeta(uname)
					if err == nil {
						chatName = dec
					}
				}
			}
		}
	}

	c.JSON(200, gin.H{
		"Success": true,
		"Data": gin.H{
			"chat_id": req.ChatID,
			"name":    chatName,
			"user_id": otherUserID,
			"type":    chatType,
		},
	})
}

func (h *Handlers) GetChat(c *gin.Context) {
	clientID, _ := c.Get("client_id")

	chatRows, err := h.db.Query(`
		SELECT chat_id FROM chat_participants 
		WHERE user_id=? ORDER BY joined_at DESC LIMIT 800
	`, clientID)
	if err != nil || len(chatRows) == 0 {
		c.JSON(200, gin.H{"Success": true, "Data": []interface{}{}, "Count": 0})
		return
	}

	var userChats []ChatData

	for _, chatRow := range chatRows {
		chatID := toInt(chatRow["chat_id"])

		chatInfo, _ := h.db.Query("SELECT type, created_at, name FROM chats WHERE id=?", chatID)
		if len(chatInfo) == 0 {
			continue
		}

		chatType := toInt(chatInfo[0]["type"])
		chatName := ""
		chatUsername := ""

		if chatType == 0 {
			others, _ := h.db.Query("SELECT user_id FROM chat_participants WHERE chat_id=? AND user_id!=? LIMIT 1", chatID, clientID)
			if len(others) > 0 {
				otherID := toInt(others[0]["user_id"])
				userData, _ := h.db.Query("SELECT username, name FROM accounts WHERE id=?", otherID)
				if len(userData) > 0 {
					if n, ok := userData[0]["name"].(string); ok && n != "" {
						dec, _ := decryptMeta(n)
						chatName = dec
					} else if u, ok := userData[0]["username"].(string); ok && u != "" {
						dec, _ := decryptMeta(u)
						chatName = dec
						chatUsername = dec
					}
				}
			}
		} else {
			chatName = toString(chatInfo[0]["name"])
		}

		lastMsg, _ := h.db.Query(`
			SELECT from_id, text, time FROM chat_message 
			WHERE chat_id=? ORDER BY time DESC LIMIT 1
		`, chatID)

		var lastMessageText interface{}
		var lastMessageTime interface{}
		var lastSenderID interface{}

		if len(lastMsg) > 0 {
			if t, ok := lastMsg[0]["text"].(string); ok && t != "" {
				dec, _ := h.encrypt.DecryptMessage(t)
				lastMessageText = dec
			}
			lastMessageTime = lastMsg[0]["time"]
			lastSenderID = lastMsg[0]["from_id"]
		}

		if lastMessageTime == nil {
			lastMessageTime = chatInfo[0]["created_at"]
		}

		notifRows, _ := h.db.Query(`
			SELECT COUNT(*) as cnt FROM chat_message 
			WHERE chat_id=? AND is_read=0 AND from_id!=?
		`, chatID, clientID)

		unread := 0
		if len(notifRows) > 0 {
			unread = toInt(notifRows[0]["cnt"])
		}

		userChats = append(userChats, ChatData{
			ChatID:          chatID,
			Name:            chatName,
			Username:        chatUsername,
			Type:            chatType,
			LastMessage:     lastMessageText,
			LastSenderID:    lastSenderID,
			LastMessageTime: lastMessageTime,
			Unread:          unread,
		})
	}

	sort.Slice(userChats, func(i, j int) bool {
		ti, _ := userChats[i].LastMessageTime.(time.Time)
		tj, _ := userChats[j].LastMessageTime.(time.Time)
		return ti.After(tj)
	})

	c.JSON(200, gin.H{
		"Success": true,
		"Data":    userChats,
		"Count":   len(userChats),
	})
}

func (h *Handlers) GetChatByUsername(c *gin.Context) {
	clientID, _ := c.Get("client_id")

	var req ChatUsernameRequest
	if err := c.ShouldBindJSON(&req); err != nil || req.Username == "" {
		c.JSON(400, gin.H{"Success": false, "Info": "Data not found"})
		return
	}

	req.Username = strings.TrimSpace(strings.ToLower(req.Username))
	usernameCrypt := encryptMeta(req.Username)

	users, err := h.db.Query("SELECT id FROM accounts WHERE username=?", usernameCrypt)
	if err != nil || len(users) == 0 {
		c.JSON(500, gin.H{"Info": "Error, Account not found"})
		return
	}

	otherID := toInt(users[0]["id"])

	chatRows, _ := h.db.Query(`
		SELECT rq1.chat_id
		FROM chat_participants rq1
		INNER JOIN chat_participants rq2 ON rq1.chat_id = rq2.chat_id
		WHERE rq1.user_id = ? AND rq2.user_id = ? AND rq1.user_id != rq2.user_id
		LIMIT 1
	`, clientID, otherID)

	if len(chatRows) > 0 {
		chatID := toInt(chatRows[0]["chat_id"])
		c.JSON(200, gin.H{
			"Success": true,
			"Data": gin.H{
				"client_id": otherID,
				"chat_id":   chatID,
			},
		})
	} else {
		c.JSON(200, gin.H{
			"Success": true,
			"Data": gin.H{
				"client_id": otherID,
				"chat_id":   nil,
			},
		})
	}
}

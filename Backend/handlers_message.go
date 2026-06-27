package main

import (
	"fmt"
	"time"

	"github.com/gin-gonic/gin"
)

func (h *Handlers) SendMessage(c *gin.Context) {
	clientID, _ := c.Get("client_id")
	fromID := clientID.(int)

	var req SendIDMessageRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(400, gin.H{"Info": "Invalid request"})
		return
	}

	if fromID == req.From {
		c.JSON(400, gin.H{"Info": "Error send message", "Log": "Error send message yourself"})
		return
	}

	chatRows, _ := h.db.Query(`
		SELECT rq1.chat_id
		FROM chat_participants rq1
		INNER JOIN chat_participants rq2 ON rq1.chat_id = rq2.chat_id
		WHERE rq1.user_id = ? AND rq2.user_id = ? AND rq1.user_id != rq2.user_id
		LIMIT 1
	`, fromID, req.From)

	var chatID int64
	if len(chatRows) > 0 {
		chatID = int64(toInt(chatRows[0]["chat_id"]))
	} else {
		newChatID, err := h.db.Exec("INSERT INTO chats (type) VALUES (0)")
		if err != nil {
			c.JSON(500, gin.H{"Info": "Error send message"})
			return
		}
		chatID = newChatID
		h.db.Exec("INSERT INTO chat_participants (chat_id, user_id) VALUES (?, ?)", chatID, fromID)
		h.db.Exec("INSERT INTO chat_participants (chat_id, user_id) VALUES (?, ?)", chatID, req.From)
	}

	encrypted, err := h.encrypt.EncryptMessage(req.Text)
	if err != nil {
		c.JSON(500, gin.H{"Info": "Encryption error"})
		return
	}

	_, err = h.db.Exec("INSERT INTO chat_message (chat_id, from_id, text) VALUES (?, ?, ?)", chatID, fromID, encrypted)
	if err != nil {
		c.JSON(500, gin.H{"Info": "Error send message"})
		return
	}

	c.JSON(200, gin.H{"Success": true, "Info": "Message was senden"})
}

func (h *Handlers) SendMessageChat(c *gin.Context) {
	clientID, _ := c.Get("client_id")
	fromID := clientID.(int)

	var req SendMessageRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(400, gin.H{"Info": "Invalid request"})
		return
	}

	check, _ := h.db.Query("SELECT 1 FROM chat_participants WHERE chat_id=? AND user_id=?", req.ChatID, fromID)
	if len(check) == 0 {
		c.JSON(400, gin.H{"Info": "Client not found in chat"})
		return
	}

	encrypted, err := h.encrypt.EncryptMessage(req.Text)
	if err != nil {
		c.JSON(500, gin.H{"Info": "Encryption error"})
		return
	}

	_, err = h.db.Exec("INSERT INTO chat_message (chat_id, from_id, text) VALUES (?, ?, ?)", req.ChatID, fromID, encrypted)
	if err != nil {
		c.JSON(500, gin.H{"Info": "Error send message"})
		return
	}

	c.JSON(200, gin.H{"Success": true, "Info": "Message was senden"})
}

func (h *Handlers) GetMessage(c *gin.Context) {
	clientID, _ := c.Get("client_id")

	var req GetMessageRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(400, gin.H{"Info": "Invalid request"})
		return
	}

	check, _ := h.db.Query("SELECT 1 FROM chat_participants WHERE chat_id=? AND user_id=?", req.ChatID, clientID)
	if len(check) == 0 {
		c.JSON(400, gin.H{"Info": "User not found in chat"})
		return
	}

	rows, err := h.db.Query(`
		SELECT id, from_id, text, time, is_read, is_edit 
		FROM chat_message WHERE chat_id=? 
		ORDER BY time ASC LIMIT 1000
	`, req.ChatID)
	if err != nil {
		c.JSON(500, gin.H{"Info": "Server error"})
		return
	}

	var messages []MessageData
	for _, row := range rows {
		msg := MessageData{}
		msg.ID = toInt(row["id"])
		msg.FromID = toInt(row["from_id"])

		if encryptedText, ok := row["text"].(string); ok && encryptedText != "" {
			decrypted, err := h.encrypt.DecryptMessage(encryptedText)
			if err == nil {
				msg.Text = decrypted
			} else {
				msg.Text = encryptedText
			}
		}

		if t, ok := row["time"].(time.Time); ok {
			msg.Time = t.Format("2006-01-02T15:04:05")
		} else {
			msg.Time = fmt.Sprintf("%v", row["time"])
		}

		msg.IsRead = toInt(row["is_read"])
		msg.IsEdit = toInt(row["is_edit"])

		messages = append(messages, msg)
	}

	if len(messages) == 0 {
		c.JSON(200, gin.H{"Success": false})
		return
	}

	c.JSON(200, gin.H{
		"Success": true,
		"Data":    messages,
		"Count":   len(messages),
	})
}

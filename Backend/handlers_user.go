package main

import (
	"strings"

	"github.com/gin-gonic/gin"
)

func (h *Handlers) GetUserMe(c *gin.Context) {
	clientID, _ := c.Get("client_id")

	rows, err := h.db.Query("SELECT username, name, email, created_at FROM accounts WHERE id=?", clientID)
	if err != nil || len(rows) == 0 {
		c.JSON(400, gin.H{"Info": "Error Get user data"})
		return
	}

	row := rows[0]
	data := UserData{}

	if u, ok := row["username"].(string); ok {
		dec, _ := decryptMeta(u)
		data.Username = dec
	}
	if n, ok := row["name"].(string); ok && n != "" {
		dec, _ := decryptMeta(n)
		data.Name = dec
	}
	if e, ok := row["email"].(string); ok && e != "" {
		dec, _ := decryptMeta(e)
		data.Email = dec
	}
	data.CreatedAt = row["created_at"]

	c.JSON(200, gin.H{
		"Success": true,
		"Data":    data,
	})
}

func (h *Handlers) GetUsernameID(c *gin.Context) {
	var req UsernameRequest
	if err := c.ShouldBindJSON(&req); err != nil || req.Username == "" {
		c.JSON(400, gin.H{"Info": "Not username, data not found"})
		return
	}

	req.Username = strings.TrimSpace(strings.ToLower(req.Username))
	usernameCrypt := encryptMeta(req.Username)

	rows, err := h.db.Query("SELECT id FROM accounts WHERE username=?", usernameCrypt)
	if err != nil || len(rows) == 0 {
		c.JSON(400, gin.H{"Info": "Data error, Account not found"})
		return
	}

	c.JSON(200, gin.H{
		"Success": true,
		"Data":    toInt(rows[0]["id"]),
	})
}

func (h *Handlers) GetUserByID(c *gin.Context) {
	var req UserIDRequest
	if err := c.ShouldBindJSON(&req); err != nil || req.ID <= 0 {
		c.JSON(403, gin.H{"Info": "Forbidden"})
		return
	}

	rows, err := h.db.Query("SELECT id, username, name FROM accounts WHERE id=?", req.ID)
	if err != nil || len(rows) == 0 {
		c.JSON(400, gin.H{"Info": "Error Get user data"})
		return
	}

	row := rows[0]
	data := UserData{}
	data.ID = toInt(row["id"])
	if u, ok := row["username"].(string); ok {
		dec, _ := decryptMeta(u)
		data.Username = dec
	}
	if n, ok := row["name"].(string); ok && n != "" {
		dec, _ := decryptMeta(n)
		data.Name = dec
	}

	c.JSON(200, gin.H{
		"Success": true,
		"Data":    data,
	})
}

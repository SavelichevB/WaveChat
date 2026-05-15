package main

import (
	"fmt"
	"strings"

	"github.com/gin-gonic/gin"
)

func (h *Handlers) Home(c *gin.Context) {
	c.JSON(200, gin.H{
		"service": "WaveChat API",
		"status":  "online",
		"version": "1.0.0.0",
	})
}

func (h *Handlers) Register(c *gin.Context) {
	var req RegisterRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(400, gin.H{"Info": "Username or Password not found"})
		return
	}

	if !validateUsername(req.Username) || !validatePassword(req.Password) {
		c.JSON(400, gin.H{"Info": "Invalid username or password", "Log": "Validation failed"})
		return
	}

	req.Username = strings.TrimSpace(strings.ToLower(req.Username))
	usernameCrypt := encryptMeta(req.Username)

	existing, err := h.db.Query("SELECT id FROM accounts WHERE username=?", usernameCrypt)
	if err != nil {
		c.JSON(500, gin.H{"Info": "Server error"})
		return
	}
	if len(existing) > 0 {
		c.JSON(400, gin.H{"Info": "Username already exists"})
		return
	}

	hash, err := hashPassword(req.Password)
	if err != nil {
		c.JSON(500, gin.H{"Info": "Server error"})
		return
	}

	userID, err := h.db.Exec("INSERT INTO accounts (username, password) VALUES (?, ?)", usernameCrypt, hash)
	if err != nil {
		c.JSON(500, gin.H{"Info": "Server error"})
		return
	}

	token, err := h.jwtManager.CreateToken(int(userID))
	if err != nil {
		c.JSON(500, gin.H{"Info": "Token creation failed"})
		return
	}

	c.SetCookie("token", token, 7*24*3600, "/", "localhost", false, true)
	c.JSON(200, gin.H{"Success": true})
}

func (h *Handlers) Login(c *gin.Context) {
	var req LoginRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(400, gin.H{"Info": "Username or Password not found"})
		return
	}

	if !validateUsername(req.Username) || !validatePassword(req.Password) {
		c.JSON(400, gin.H{"Info": "Invalid username or password", "Log": "Validation failed"})
		return
	}

	req.Username = strings.TrimSpace(strings.ToLower(req.Username))
	usernameCrypt := encryptMeta(req.Username)

	users, err := h.db.Query("SELECT id, password FROM accounts WHERE username=?", usernameCrypt)
	if err != nil || len(users) == 0 {
		c.JSON(400, gin.H{"Info": "User not found"})
		return
	}

	user := users[0]
	userID, _ := toInt64(user["id"])
	storedHash, _ := user["password"].(string)

	if !checkPassword(req.Password, storedHash) {
		c.JSON(400, gin.H{"Info": "Invalid password"})
		return
	}

	token, err := h.jwtManager.CreateToken(int(userID))
	if err != nil {
		c.JSON(500, gin.H{"Info": "Token creation failed"})
		return
	}

	c.SetCookie("token", token, 7*24*3600, "/", "localhost", false, true)
	c.JSON(200, gin.H{"Success": true})
}

func (h *Handlers) CheckAuth(c *gin.Context) {
	clientID, exists := c.Get("client_id")
	if !exists {
		c.JSON(403, gin.H{"Info": "Error verify token"})
		return
	}
	c.JSON(200, gin.H{"Success": true, "Client_id": fmt.Sprintf("%v", clientID)})
}

func (h *Handlers) Logout(c *gin.Context) {
	c.SetCookie("token", "", -1, "/", "localhost", false, true)
	c.JSON(200, gin.H{"Success": true})
}

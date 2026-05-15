package main

import (
	"log"

	"github.com/gin-gonic/gin"
)

func main() {
	cfg := LoadConfig()

	encrypt, err := NewEncrypt(cfg.EncryptionKey)
	if err != nil {
		log.Fatalf("Encryption init failed: %v", err)
	}

	db, err := NewDB(cfg)
	if err != nil {
		log.Fatalf("Database init failed: %v", err)
	}
	log.Println("MySQL connected")

	jwtManager := NewJWTManager(cfg.JWTSecret)

	hub := NewHub(jwtManager, db, encrypt)
	handlers := NewHandlers(db, encrypt, jwtManager)

	r := gin.Default()

	r.Use(func(c *gin.Context) {
		c.Set("jwtManager", jwtManager)
		c.Next()
	})

	r.GET("/", handlers.Home)

	auth := r.Group("/auth")
	{
		auth.POST("/reg", handlers.Register)
		auth.POST("/login", handlers.Login)
		auth.GET("/check", JWTAuthMiddleware(jwtManager), handlers.CheckAuth)
		auth.POST("/logout", handlers.Logout)
	}

	msg := r.Group("/message")
	msg.Use(JWTAuthMiddleware(jwtManager))
	{
		msg.POST("/send/id", handlers.SendMessage)
		msg.POST("/send/chat", handlers.SendMessageChat)
		msg.POST("/get", handlers.GetMessage)
	}

	chat := r.Group("/chat")
	chat.Use(JWTAuthMiddleware(jwtManager))
	{
		chat.GET("/get", handlers.GetChat)
		chat.POST("/info", handlers.GetChatInfo)
		chat.POST("/username", handlers.GetChatByUsername)
	}

	users := r.Group("/users")
	{
		users.GET("/me", JWTAuthMiddleware(jwtManager), handlers.GetUserMe)
		users.POST("/username/get", handlers.GetUsernameID)
		users.POST("/get", handlers.GetUserByID)
	}

	r.GET("/ws", func(c *gin.Context) {
		hub.HandleWS(c.Writer, c.Request)
	})

	log.Printf("Server starting on port %s", cfg.ServerPort)
	if err := r.Run(":" + cfg.ServerPort); err != nil {
		log.Fatalf("Server failed: %v", err)
	}
}

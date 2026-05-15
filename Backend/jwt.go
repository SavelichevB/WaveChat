package main

import (
	"fmt"
	"strconv"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/golang-jwt/jwt/v5"
)

type JWTManager struct {
	secret []byte
}

func NewJWTManager(secret string) *JWTManager {
	return &JWTManager{secret: []byte(secret)}
}

func (j *JWTManager) CreateToken(userID int) (string, error) {
	claims := jwt.MapClaims{
		"sub": strconv.Itoa(userID),
		"exp": time.Now().Add(7 * 24 * time.Hour).Unix(),
		"iat": time.Now().Unix(),
	}
	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	return token.SignedString(j.secret)
}

func (j *JWTManager) ParseToken(tokenStr string) (int, error) {
	token, err := jwt.Parse(tokenStr, func(token *jwt.Token) (interface{}, error) {
		if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
			return nil, fmt.Errorf("unexpected signing method: %v", token.Header["alg"])
		}
		return j.secret, nil
	})
	if err != nil {
		return 0, err
	}

	claims, ok := token.Claims.(jwt.MapClaims)
	if !ok || !token.Valid {
		return 0, fmt.Errorf("invalid token")
	}

	sub, ok := claims["sub"].(string)
	if !ok {
		return 0, fmt.Errorf("invalid subject")
	}

	id, err := strconv.Atoi(sub)
	if err != nil {
		return 0, err
	}

	return id, nil
}

func JWTAuthMiddleware(jwtManager *JWTManager) gin.HandlerFunc {
	return func(c *gin.Context) {
		token, err := c.Cookie("token")
		if err != nil || token == "" {
			c.AbortWithStatusJSON(401, gin.H{"Info": "Not token"})
			return
		}

		userID, err := jwtManager.ParseToken(token)
		if err != nil {
			c.AbortWithStatusJSON(401, gin.H{"Info": "Invalid token"})
			return
		}

		c.Set("client_id", userID)
		c.Next()
	}
}

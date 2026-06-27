package main

import "os"

type Config struct {
	DBHost        string
	DBPort        string
	DBUser        string
	DBPassword    string
	DBName        string
	JWTSecret     string
	EncryptionKey string
	ServerPort    string
}

func LoadConfig() *Config {
	return &Config{
		DBHost:        getEnv("DB_HOST", "localhost"),
		DBPort:        getEnv("DB_PORT", "3306"),
		DBUser:        getEnv("DB_USER", "root"),
		DBPassword:    getEnv("DB_PASSWORD", ""),
		DBName:        getEnv("DB_NAME", "wave_chat"),
		JWTSecret:     getEnv("JWT_SECRET", "WaveMini"),
		EncryptionKey: getEnv("ENCRYPTION_KEY", "AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8="),
		ServerPort:    getEnv("SERVER_PORT", "3333"),
	}
}

func getEnv(key, fallback string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return fallback
}

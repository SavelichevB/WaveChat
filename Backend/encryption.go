package main

import (
	"crypto/aes"
	"crypto/cipher"
	"crypto/rand"
	"encoding/base64"
	"errors"
	"io"
)

type Encrypt struct {
	key []byte
}

func NewEncrypt(keyBase64 string) (*Encrypt, error) {
	key, err := base64.StdEncoding.DecodeString(keyBase64)
	if err != nil {
		return nil, errors.New("invalid encryption key")
	}
	if len(key) != 32 {
		return nil, errors.New("encryption key must be 32 bytes")
	}
	return &Encrypt{key: key}, nil
}

func (e *Encrypt) EncryptMessage(text string) (string, error) {
	iv := make([]byte, aes.BlockSize)
	if _, err := io.ReadFull(rand.Reader, iv); err != nil {
		return "", err
	}

	block, err := aes.NewCipher(e.key)
	if err != nil {
		return "", err
	}

	paddedText := pkcs7Pad([]byte(text), aes.BlockSize)

	cbc := cipher.NewCBCEncrypter(block, iv)
	ciphertext := make([]byte, len(paddedText))
	cbc.CryptBlocks(ciphertext, paddedText)

	result := append(iv, ciphertext...)
	return base64.StdEncoding.EncodeToString(result), nil
}

func (e *Encrypt) DecryptMessage(data string) (string, error) {
	encrypted, err := base64.StdEncoding.DecodeString(data)
	if err != nil {
		return "", err
	}

	if len(encrypted) < aes.BlockSize {
		return "", errors.New("ciphertext too short")
	}

	iv := encrypted[:aes.BlockSize]
	ciphertext := encrypted[aes.BlockSize:]

	block, err := aes.NewCipher(e.key)
	if err != nil {
		return "", err
	}

	cbc := cipher.NewCBCDecrypter(block, iv)
	paddedText := make([]byte, len(ciphertext))
	cbc.CryptBlocks(paddedText, ciphertext)

	text, err := pkcs7Unpad(paddedText, aes.BlockSize)
	if err != nil {
		return data, nil
	}

	return string(text), nil
}

func pkcs7Pad(data []byte, blockSize int) []byte {
	padding := blockSize - len(data)%blockSize
	padText := make([]byte, padding)
	for i := range padText {
		padText[i] = byte(padding)
	}
	return append(data, padText...)
}

func pkcs7Unpad(data []byte, blockSize int) ([]byte, error) {
	if len(data) == 0 {
		return nil, errors.New("empty data")
	}
	padding := int(data[len(data)-1])
	if padding > len(data) || padding > blockSize || padding == 0 {
		return nil, errors.New("invalid padding")
	}
	return data[:len(data)-padding], nil
}

func encryptMeta(data string) string {
	return base64.StdEncoding.EncodeToString([]byte(data))
}

func decryptMeta(data string) (string, error) {
	decoded, err := base64.StdEncoding.DecodeString(data)
	if err != nil {
		return "", err
	}
	return string(decoded), nil
}

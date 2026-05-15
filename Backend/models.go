package main

type Response struct {
	Success  bool        `json:"Success,omitempty"`
	Data     interface{} `json:"Data,omitempty"`
	Info     string      `json:"Info,omitempty"`
	Count    int         `json:"Count,omitempty"`
	ClientID string      `json:"Client_id,omitempty"`
	Log      string      `json:"Log,omitempty"`
}

type RegisterRequest struct {
	Username string `json:"username"`
	Password string `json:"password"`
}

type LoginRequest struct {
	Username string `json:"username"`
	Password string `json:"password"`
}

type SendMessageRequest struct {
	ChatID int    `json:"chat_id"`
	Text   string `json:"text"`
}

type SendIDMessageRequest struct {
	From int    `json:"from"`
	Text string `json:"text"`
}

type GetMessageRequest struct {
	ChatID int `json:"chat_id"`
}

type ChatInfoRequest struct {
	ChatID int `json:"chat_id"`
}

type ChatUsernameRequest struct {
	Username string `json:"username"`
}

type UserIDRequest struct {
	ID int `json:"id"`
}

type UsernameRequest struct {
	Username string `json:"username"`
}

type ChatData struct {
	ChatID          int         `json:"chat_id"`
	Name            string      `json:"name"`
	Username        string      `json:"username,omitempty"`
	Type            int         `json:"type"`
	LastMessage     interface{} `json:"last_message,omitempty"`
	LastSenderID    interface{} `json:"last_sender_id,omitempty"`
	LastMessageTime interface{} `json:"last_message_time,omitempty"`
	Unread          int         `json:"unread"`
}

type MessageData struct {
	ID      int    `json:"id"`
	FromID  int    `json:"from_id"`
	Text    string `json:"text"`
	Time    string `json:"time"`
	IsRead  int    `json:"is_read"`
	IsEdit  int    `json:"is_edit"`
}

type UserData struct {
	ID        int         `json:"id,omitempty"`
	Username  string      `json:"username,omitempty"`
	Name      interface{} `json:"name,omitempty"`
	Email     interface{} `json:"email,omitempty"`
	CreatedAt interface{} `json:"created_at,omitempty"`
}

type WsMessage struct {
	Type    string `json:"type"`
	ChatID  int    `json:"chat_id,omitempty"`
	ToID    int    `json:"to_id,omitempty"`
	Text    string `json:"text,omitempty"`
	TempID  int64  `json:"temp_id,omitempty"`
	MessageID int  `json:"message_id,omitempty"`
	UserID  int    `json:"user_id,omitempty"`
}

type WsOutgoing struct {
	Type      string      `json:"type"`
	ID        interface{} `json:"id,omitempty"`
	FromID    int         `json:"from_id,omitempty"`
	Text      string      `json:"text,omitempty"`
	Time      string      `json:"time,omitempty"`
	ChatID    interface{} `json:"chat_id,omitempty"`
	TempID    int64       `json:"temp_id,omitempty"`
	Success   bool        `json:"success,omitempty"`
	MessageID interface{} `json:"message_id,omitempty"`
	Error     string      `json:"error,omitempty"`
	UserID    int         `json:"user_id,omitempty"`
	Count     int         `json:"count,omitempty"`
}

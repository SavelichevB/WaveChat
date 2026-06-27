package main

type Handlers struct {
	db         *DB
	encrypt    *Encrypt
	jwtManager *JWTManager
}

func NewHandlers(db *DB, enc *Encrypt, jm *JWTManager) *Handlers {
	return &Handlers{db: db, encrypt: enc, jwtManager: jm}
}

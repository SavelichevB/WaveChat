package main

import (
	"database/sql"
	"fmt"

	_ "github.com/go-sql-driver/mysql"
)

type DB struct {
	pool *sql.DB
}

func NewDB(cfg *Config) (*DB, error) {
	dsn := fmt.Sprintf("%s:%s@tcp(%s:%s)/%s?charset=utf8mb4&parseTime=true&loc=Local",
		cfg.DBUser, cfg.DBPassword, cfg.DBHost, cfg.DBPort, cfg.DBName)

	pool, err := sql.Open("mysql", dsn)
	if err != nil {
		return nil, fmt.Errorf("db open: %w", err)
	}

	pool.SetMaxOpenConns(20)
	pool.SetMaxIdleConns(10)

	if err := pool.Ping(); err != nil {
		return nil, fmt.Errorf("db ping: %w", err)
	}

	return &DB{pool: pool}, nil
}

func (d *DB) Query(query string, args ...interface{}) ([]map[string]interface{}, error) {
	rows, err := d.pool.Query(query, args...)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	cols, err := rows.Columns()
	if err != nil {
		return nil, err
	}

	var result []map[string]interface{}

	for rows.Next() {
		values := make([]interface{}, len(cols))
		valuePtrs := make([]interface{}, len(cols))
		for i := range cols {
			valuePtrs[i] = &values[i]
		}

		if err := rows.Scan(valuePtrs...); err != nil {
			return nil, err
		}

		row := make(map[string]interface{})
		for i, col := range cols {
			val := values[i]
			b, ok := val.([]byte)
			if ok {
				row[col] = string(b)
			} else {
				row[col] = val
			}
		}
		result = append(result, row)
	}

	return result, nil
}

func (d *DB) Exec(query string, args ...interface{}) (int64, error) {
	result, err := d.pool.Exec(query, args...)
	if err != nil {
		return 0, err
	}
	id, err := result.LastInsertId()
	if err != nil {
		return 0, err
	}
	return id, nil
}

func (d *DB) ExecAffected(query string, args ...interface{}) (int64, error) {
	result, err := d.pool.Exec(query, args...)
	if err != nil {
		return 0, err
	}
	return result.RowsAffected()
}

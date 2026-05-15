package main

import "strings"

var forbiddenSymbols = []string{
	"<", ">", "&", "'", "\"", ";", "--", "=",
	"/*", "*/", "@@", "xp_", "sp_",
	"javascript:", "onclick=", "onload=",
	"union select", "drop table", "insert into",
}

func validateData(input string) bool {
	for _, sym := range forbiddenSymbols {
		if strings.Contains(input, sym) {
			return false
		}
	}
	return true
}

func validateUsername(username string) bool {
	if !validateData(username) {
		return false
	}
	length := len(username)
	return length >= 3 && length <= 100
}

func validatePassword(password string) bool {
	if !validateData(password) {
		return false
	}
	length := len(password)
	return length >= 8 && length <= 100
}

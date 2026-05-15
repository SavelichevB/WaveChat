package main

import "fmt"

func toInt64(v interface{}) (int64, error) {
	switch val := v.(type) {
	case int64:
		return val, nil
	case float64:
		return int64(val), nil
	case int:
		return int64(val), nil
	case string:
		var i int64
		_, err := fmt.Sscanf(val, "%d", &i)
		return i, err
	default:
		return 0, fmt.Errorf("cannot convert %T to int64", v)
	}
}

func toInt(v interface{}) int {
	i, _ := toInt64(v)
	return int(i)
}

func toString(v interface{}) string {
	if v == nil {
		return ""
	}
	if s, ok := v.(string); ok {
		return s
	}
	return fmt.Sprintf("%v", v)
}

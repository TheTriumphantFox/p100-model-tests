package octal

import (
	"errors"
)

func ParseOctal(input string) (int64, error) {
	var result int64
	for _, char := range input {
		if char < '0' || char > '7' {
			return 0, errors.New("invalid octal digit")
		}
		result = result*8 + int64(char-'0')
	}
	return result, nil
}

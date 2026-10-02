package octal

import "errors"

func ParseOctal(input string) (int64, error) {
	var n int64
	for _, c := range input {
		if c < '0' || c > '7' {
			return 0, errors.New("invalid octal digit")
		}
		n = n*8 + int64(c-'0')
	}
	return n, nil
}

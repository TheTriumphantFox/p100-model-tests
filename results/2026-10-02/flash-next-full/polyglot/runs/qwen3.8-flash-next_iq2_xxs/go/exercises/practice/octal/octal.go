package octal

import (
	"fmt"
	"strconv"
)

func ParseOctal(octal string) (int64, error) {
	decimal := int64(0)
	
	// Check for invalid characters (non-octal digits)
	for _, c := range octal {
		if c < '0' || c > '7' {
			return 0, fmt.Errorf("invalid octal input: %s", octal)
		}
	}

	// Calculate decimal value using first principles
	for _, c := range octal {
		decimal = decimal*8 + int64(c-'0')
	}

	return decimal, nil
}

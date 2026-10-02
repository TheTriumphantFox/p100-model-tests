package cryptosquare

import (
	"math"
	"strings"
	"unicode"
)

func Encode(pt string) string {
	var sb strings.Builder
	for _, r := range pt {
		if unicode.IsLetter(r) || unicode.IsDigit(r) {
			sb.WriteRune(unicode.ToLower(r))
		}
	}
	normalized := sb.String()
	
	if len(normalized) == 0 {
		return ""
	}
	
	c := int(math.Ceil(math.Sqrt(float64(len(normalized)))))
	r := int(math.Ceil(float64(len(normalized)) / float64(c)))
	
	var encoded strings.Builder
	for col := 0; col < c; col++ {
		if col > 0 {
			encoded.WriteByte(' ')
		}
		for row := 0; row < r; row++ {
			idx := row*c + col
			if idx < len(normalized) {
				encoded.WriteByte(normalized[idx])
			} else {
				encoded.WriteByte(' ')
			}
		}
	}
	
	return encoded.String()
}

package cryptosquare

import (
	"math"
	"strings"
	"unicode"
)

func Encode(pt string) string {
	// Normalize the text: remove spaces and punctuation, downcase
	var normalized strings.Builder
	for _, r := range pt {
		if unicode.IsLetter(r) || unicode.IsDigit(r) {
			normalized.WriteRune(unicode.ToLower(r))
		}
	}
	normalizedText := normalized.String()
	length := len(normalizedText)

	if length == 0 {
		return ""
	}

	// Calculate dimensions of the rectangle
	// c >= r and c - r <= 1 and r * c >= length
	c := int(math.Ceil(math.Sqrt(float64(length))))
	r := int(math.Ceil(float64(length) / float64(c)))

	// Read down the columns to form the encoded text
	var encoded strings.Builder
	for i := 0; i < c; i++ {
		for j := 0; j < r; j++ {
			idx := j*c + i
			if idx < length {
				encoded.WriteByte(normalizedText[idx])
			} else {
				encoded.WriteByte(' ')
			}
		}
		if i < c-1 {
			encoded.WriteByte(' ')
		}
	}

	return encoded.String()
}

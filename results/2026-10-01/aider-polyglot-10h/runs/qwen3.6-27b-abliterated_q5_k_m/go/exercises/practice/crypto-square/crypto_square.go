package cryptosquare

import (
	"math"
	"strings"
	"unicode"
)

func Encode(pt string) string {
	normalized := normalize(pt)
	if len(normalized) == 0 {
		return ""
	}

	c, r := dimensions(len(normalized))

	// Pad the normalized string with spaces to fill the rectangle
	padded := normalized + strings.Repeat(" ", c*r-len(normalized))

	var chunks []string
	for i := 0; i < c; i++ {
		var chunk strings.Builder
		for j := 0; j < r; j++ {
			chunk.WriteByte(padded[j*c+i])
		}
		chunks = append(chunks, chunk.String())
	}

	return strings.Join(chunks, " ")
}

func normalize(pt string) string {
	var sb strings.Builder
	for _, r := range pt {
		if unicode.IsLetter(r) || unicode.IsDigit(r) {
			sb.WriteRune(unicode.ToLower(r))
		}
	}
	return sb.String()
}

func dimensions(length int) (c, r int) {
	c = int(math.Ceil(math.Sqrt(float64(length))))
	if c*(c-1) >= length {
		r = c - 1
	} else {
		r = c
	}
	return c, r
}

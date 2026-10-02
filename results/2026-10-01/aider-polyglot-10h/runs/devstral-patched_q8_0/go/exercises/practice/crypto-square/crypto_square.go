package cryptosquare

import (
	"math"
	"strings"
	"unicode"
)

func Encode(pt string) string {
	// Normalize the input: remove spaces and punctuation, and down-case
	normalized := normalize(pt)

	// Calculate the dimensions of the rectangle
	c, r := calculateDimensions(len(normalized))

	// Build the rectangle
	rectangle := buildRectangle(normalized, c, r)

	// Read the columns to form the encoded message
	encoded := readColumns(rectangle, c, r)

	return encoded
}

func normalize(s string) string {
	var result strings.Builder
	for _, r := range s {
		if unicode.IsLetter(r) || unicode.IsNumber(r) {
			result.WriteRune(unicode.ToLower(r))
		}
	}
	return result.String()
}

func calculateDimensions(length int) (int, int) {
	c := int(math.Ceil(math.Sqrt(float64(length))))
	r := int(math.Floor(math.Sqrt(float64(length))))

	// Ensure c >= r and c - r <= 1
	if c < r {
		c, r = r, c
	}
	if c-r > 1 {
		c = r + 1
	}

	return c, r
}

func buildRectangle(s string, c, r int) [][]rune {
	rectangle := make([][]rune, r)
	for i := 0; i < r; i++ {
		start := i * c
		end := start + c
		if end > len(s) {
			end = len(s)
		}
		row := make([]rune, c)
		for j := 0; j < c; j++ {
			if start+j < len(s) {
				row[j] = rune(s[start+j])
			} else {
				row[j] = ' '
			}
		}
		rectangle[i] = row
	}
	return rectangle
}

func readColumns(rectangle [][]rune, c, r int) string {
	var result strings.Builder
	for col := 0; col < c; col++ {
		for row := 0; row < r; row++ {
			result.WriteRune(rectangle[row][col])
		}
		if col < c-1 {
			result.WriteString(" ")
		}
	}
	return result.String()
}

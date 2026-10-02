package cryptosquare

import (
	"math"
	"strings"
	"unicode"
)

func Encode(pt string) string {
	// Normalize the input: remove non-alphanumeric characters and downcase
	var normalized []rune
	for _, r := range pt {
		if unicode.IsLetter(r) || unicode.IsNumber(r) {
			normalized = append(normalized, unicode.ToLower(r))
		}
	}

	length := len(normalized)
	if length == 0 {
		return ""
	}

	// Calculate dimensions r and c
	// c is the smallest integer such that c >= r, c - r <= 1, and r * c >= length
	c := int(math.Ceil(math.Sqrt(float64(length))))
	r := c
	if r*c < length {
		r++
	}
	// Ensure c >= r
	if c < r {
		c = r
	}
	// Re-verify constraints just in case, though the above logic usually holds
	// Actually, the standard way is:
	// c = ceil(sqrt(length))
	// r = ceil(length / c)
	// This ensures r*c >= length and c >= r (mostly) and c-r <= 1.
	
	// Let's stick to the robust calculation:
	c = int(math.Ceil(math.Sqrt(float64(length))))
	r = int(math.Ceil(float64(length) / float64(c)))
	
	// If r > c, swap? No, the problem says c >= r.
	// If length is a perfect square, r=c.
	// If not, c is usually the larger one or equal.
	// Example: len=54. sqrt(54)=7.34. c=8. r=ceil(54/8)=7. c>=r (8>=7). c-r=1. Correct.
	// Example: len=1. sqrt(1)=1. c=1. r=1. Correct.
	// Example: len=2. sqrt(2)=1.41. c=2. r=ceil(2/2)=1. c>=r (2>=1). c-r=1. Correct.
	// Example: len=3. sqrt(3)=1.73. c=2. r=ceil(3/2)=2. c>=r (2>=2). c-r=0. Correct.
	// Example: len=4. sqrt(4)=2. c=2. r=2. Correct.
	// Example: len=5. sqrt(5)=2.23. c=3. r=ceil(5/3)=2. c>=r (3>=2). c-r=1. Correct.
	
	// Construct the encoded string
	chunks := make([]string, c)
	for i := 0; i < c; i++ {
		var chunk []rune
		for j := 0; j < r; j++ {
			idx := j*c + i
			if idx < length {
				chunk = append(chunk, normalized[idx])
			} else {
				chunk = append(chunk, ' ')
			}
		}
		chunks[i] = string(chunk)
	}

	return strings.Join(chunks, " ")
}

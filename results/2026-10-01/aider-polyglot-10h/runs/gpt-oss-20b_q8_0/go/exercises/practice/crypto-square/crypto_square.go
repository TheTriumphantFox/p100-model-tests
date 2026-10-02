package cryptosquare

import (
	"math"
	"regexp"
	"strings"
)

// Encode transforms the given plaintext into its square code cipher.
// The plaintext is first normalized by removing all non-alphanumeric characters
// and converting to lower case.  The normalized text is then arranged
// into a rectangle that is as close to a square as possible.  The
// rectangle dimensions are chosen such that:
//   * r * c >= len(normalized)
//   * c >= r
//   * c - r <= 1
// The ciphertext is produced by reading the rectangle column‑wise
// from left to right.  Finally the ciphertext is split into c
// chunks of r characters each, separated by a single space.  If the
// ciphertext is shorter than r*c, the missing characters are
// represented by a trailing space in the last chunks.
func Encode(pt string) string {
	// 1. Normalize: keep only letters and digits, lower case.
	re := regexp.MustCompile(`[a-zA-Z0-9]`)
	normalized := strings.ToLower(strings.Join(re.FindAllString(pt, -1), ""))

	if len(normalized) == 0 {
		return ""
	}

	// 2. Determine rectangle dimensions.
	n := len(normalized)
	// Start with floor(sqrt(n)) as rows.
	r := int(math.Floor(math.Sqrt(float64(n))))
	// Compute columns as ceil(n / r).
	c := int(math.Ceil(float64(n) / float64(r)))

	// Ensure c >= r and c - r <= 1
	if c < r {
		c = r
	}
	if c-r > 1 {
		c = r + 1
	}

	// 3. Build the rectangle row by row.
	rows := make([]string, r)
	for i := 0; i < r; i++ {
		start := i * c
		end := start + c
		if end > n {
			end = n
		}
		rows[i] = normalized[start:end]
	}

	// 4. Read column-wise to produce ciphertext.
	var sb strings.Builder
	for col := 0; col < c; col++ {
		for row := 0; row < r; row++ {
			if col < len(rows[row]) {
				sb.WriteByte(rows[row][col])
			}
		}
	}
	cipher := sb.String()

	// 5. Pad ciphertext to length r*c with spaces if necessary.
	totalLen := r * c
	if len(cipher) < totalLen {
		cipher += strings.Repeat(" ", totalLen-len(cipher))
	}

	// 6. Split into c chunks of r characters each, separated by spaces.
	chunks := make([]string, c)
	for i := 0; i < c; i++ {
		start := i * r
		end := start + r
		chunks[i] = cipher[start:end]
	}

	return strings.Join(chunks, " ")
}

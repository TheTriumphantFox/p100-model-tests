package palindrome

import (
	"errors"
	"fmt"
	"strconv"
)

// Define Product type here.
type Product struct {
	Value          int
	Factorizations [][2]int
}

func Products(fmin, fmax int) (Product, Product, error) {
	if fmin > fmax {
		return Product{}, Product{}, errors.New("fmin > fmax")
	}

	var minProduct Product
	var maxProduct Product
	minFound := false
	maxFound := false

	// Iterate through all pairs (i, j) such that fmin <= i <= j <= fmax
	for i := fmin; i <= fmax; i++ {
		for j := i; j <= fmax; j++ {
			p := i * j

			// Optimization: If we are looking for min and current p > maxProduct.Value (if found),
			// and we are iterating upwards, we might not need to check further for min?
			// Actually, simple iteration is safer given constraints usually aren't huge in these exercises.
			// But let's just collect all palindromes first or track min/max on the fly.
			// Tracking on the fly is more efficient.

			if isPalindrome(p) {
				// Check for min
				if !minFound || p < minProduct.Value {
					minProduct = Product{Value: p, Factorizations: [][2]int{{i, j}}}
					minFound = true
				} else if p == minProduct.Value {
					minProduct.Factorizations = append(minProduct.Factorizations, [2]int{i, j})
				}

				// Check for max
				if !maxFound || p > maxProduct.Value {
					maxProduct = Product{Value: p, Factorizations: [][2]int{{i, j}}}
					maxFound = true
				} else if p == maxProduct.Value {
					maxProduct.Factorizations = append(maxProduct.Factorizations, [2]int{i, j})
				}
			}
		}
	}

	if !minFound {
		return Product{}, Product{}, fmt.Errorf("no palindromes in range")
	}

	return minProduct, maxProduct, nil
}

func isPalindrome(n int) bool {
	s := strconv.Itoa(n)
	length := len(s)
	for i := 0; i < length/2; i++ {
		if s[i] != s[length-1-i] {
			return false
		}
	}
	return true
}

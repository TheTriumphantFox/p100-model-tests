package palindrome

import (
	"errors"
	"sort"
)

// Product represents a palindromic product and all factor pairs that produce it.
type Product struct {
	Value          int
	Factorizations [][2]int
}

// isPalindrome checks whether an integer is a palindrome.
func isPalindrome(n int) bool {
	if n < 0 {
		return false
	}
	orig := n
	reversed := 0
	for n > 0 {
		reversed = reversed*10 + n%10
		n /= 10
	}
	return orig == reversed
}

// Products returns the smallest and largest palindromic products that can be
// formed by multiplying two numbers in the inclusive range [fmin, fmax].
// If no palindromic product exists, an error is returned.
func Products(fmin, fmax int) (Product, Product, error) {
	if fmin > fmax || fmin < 1 {
		return Product{}, Product{}, errors.New("invalid range")
	}

	// Map from palindrome value to its factor pairs.
	palMap := make(map[int][][2]int)

	for i := fmin; i <= fmax; i++ {
		for j := i; j <= fmax; j++ { // j starts at i to avoid duplicate pairs
			prod := i * j
			if isPalindrome(prod) {
				palMap[prod] = append(palMap[prod], [2]int{i, j})
			}
		}
	}

	if len(palMap) == 0 {
		return Product{}, Product{}, errors.New("no palindromic product found")
	}

	// Extract sorted keys to find min and max.
	keys := make([]int, 0, len(palMap))
	for k := range palMap {
		keys = append(keys, k)
	}
	sort.Ints(keys)

	minProd := Product{
		Value:          keys[0],
		Factorizations: palMap[keys[0]],
	}
	maxProd := Product{
		Value:          keys[len(keys)-1],
		Factorizations: palMap[keys[len(keys)-1]],
	}

	return minProd, maxProd, nil
}

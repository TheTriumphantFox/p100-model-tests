package palindrome

import (
	"errors"
	"strconv"
)

// Define Product type here.
type Product struct {
	Palindrome      int
	Factorizations  [][2]int
}

func Products(fmin, fmax int) (Product, Product, error) {
	if fmin > fmax {
		return Product{}, Product{}, errors.New("fmin > fmax")
	}

	palindromes := make(map[int][][2]int)

	for i := fmin; i <= fmax; i++ {
		for j := i; j <= fmax; j++ {
			p := i * j
			if isPalindrome(p) {
				palindromes[p] = append(palindromes[p], [2]int{i, j})
			}
		}
	}

	if len(palindromes) == 0 {
		return Product{}, Product{}, errors.New("no palindromes found")
	}

	minVal := -1
	maxVal := -1

	for p := range palindromes {
		if minVal == -1 || p < minVal {
			minVal = p
		}
		if maxVal == -1 || p > maxVal {
			maxVal = p
		}
	}

	smallest := Product{Palindrome: minVal, Factorizations: palindromes[minVal]}
	largest := Product{Palindrome: maxVal, Factorizations: palindromes[maxVal]}

	return smallest, largest, nil
}

func isPalindrome(n int) bool {
	s := strconv.Itoa(n)
	len := len(s)
	for i := 0; i < len/2; i++ {
		if s[i] != s[len-1-i] {
			return false
		}
	}
	return true
}

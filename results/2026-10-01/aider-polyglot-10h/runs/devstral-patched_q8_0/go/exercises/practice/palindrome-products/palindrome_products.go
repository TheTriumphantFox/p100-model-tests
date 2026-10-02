package palindrome

import (
	"strconv"
	"sort"
)

// Product represents a palindrome product with its factors
type Product struct {
	Value int
	Factorizations []FactorPair
}

// FactorPair represents a pair of factors that multiply to form a palindrome product
type FactorPair struct {
	A int
	B int
}

// isPalindrome checks if a number is a palindrome
func isPalindrome(n int) bool {
	s := strconv.Itoa(n)
	for i := 0; i < len(s)/2; i++ {
		if s[i] != s[len(s)-1-i] {
			return false
		}
	}
	return true
}

// Products finds the smallest and largest palindromes within the given range
func Products(fmin, fmax int) (Product, Product, error) {
	if fmin <= 0 || fmax <= 0 {
		return Product{}, Product{}, nil
	}
	if fmin > fmax {
		return Product{}, Product{}, nil
	}

	var palindromes = make(map[int][]FactorPair)

	// Generate all possible products in the range
	for i := fmin; i <= fmax; i++ {
		for j := fmin; j <= fmax; j++ {
			product := i * j
			if isPalindrome(product) {
				palindromes[product] = append(palindromes[product], FactorPair{A: i, B: j})
			}
		}
	}

	if len(palindromes) == 0 {
		return Product{}, Product{}, nil
	}

	// Find smallest and largest palindromes
	var smallest Product
	var largest Product

	for product, factors := range palindromes {
		// Remove duplicate factor pairs (like (a,b) and (b,a))
		uniqueFactors := removeDuplicatePairs(factors)

		if smallest.Value == 0 || product < smallest.Value {
			smallest = Product{Value: product, Factorizations: uniqueFactors}
		}
		if largest.Value == 0 || product > largest.Value {
			largest = Product{Value: product, Factorizations: uniqueFactors}
		}
	}

	return smallest, largest, nil
}

// removeDuplicatePairs removes duplicate factor pairs (like (a,b) and (b,a))
func removeDuplicatePairs(pairs []FactorPair) []FactorPair {
	unique := make(map[string]FactorPair)
	for _, p := range pairs {
		// Use the smaller number first to identify duplicates
		a, b := p.A, p.B
		if a > b {
			a, b = b, a
		}
		key := strconv.Itoa(a) + "," + strconv.Itoa(b)
		unique[key] = FactorPair{A: a, B: b}
	}

	// Convert back to slice and sort
	result := make([]FactorPair, 0, len(unique))
	for _, p := range unique {
		result = append(result, p)
	}
	sort.Slice(result, func(i, j int) bool {
		if result[i].A == result[j].A {
			return result[i].B < result[j].B
		}
		return result[i].A < result[j].A
	})

	return result
}

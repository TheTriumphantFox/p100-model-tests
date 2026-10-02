package palindrome

import (
	"errors"
	"fmt"
)

// Define Product type here.
type Product struct {
	Product       int
	Factorizations [][2]int
}

func isPalindrome(n int) bool {
	if n < 0 {
		return false
	}
	original := n
	reversed := 0
	for n > 0 {
		reversed = reversed*10 + n%10
		n /= 10
	}
	return original == reversed
}

func Products(fmin, fmax int) (Product, Product, error) {
	if fmin > fmax {
		return Product{}, Product{}, errors.New("fmin must be <= fmax")
	}

	var smallest, largest Product
	smallest.Product = -1
	largest.Product = -1

	for i := fmin; i <= fmax; i++ {
		for j := i; j <= fmax; j++ {
			product := i * j
			if isPalindrome(product) {
				if product < smallest.Product || smallest.Product == -1 {
					smallest.Product = product
					smallest.Factorizations = [][2]int{{i, j}}
				} else if product == smallest.Product {
					smallest.Factorizations = append(smallest.Factorizations, [2]int{i, j})
				}

				if product > largest.Product {
					largest.Product = product
					largest.Factorizations = [][2]int{{i, j}}
				} else if product == largest.Product {
					largest.Factorizations = append(largest.Factorizations, [2]int{i, j})
				}
			}
		}
	}

	if smallest.Product == -1 {
		return Product{}, Product{}, fmt.Errorf("no palindromes found in range [%d, %d]", fmin, fmax)
	}

	return smallest, largest, nil
}

package palindrome

import "fmt"

// Define Product type here.
type Product struct {
	Value         int
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
		return Product{}, Product{}, fmt.Errorf("given fmin is greater than fmax")
	}

	minProduct := Product{Value: -1}
	maxProduct := Product{Value: -1}

	for i := fmin; i <= fmax; i++ {
		for j := i; j <= fmax; j++ {
			product := i * j
			if isPalindrome(product) {
				if minProduct.Value == -1 || product < minProduct.Value {
					minProduct.Value = product
					minProduct.Factorizations = [][2]int{{i, j}}
				} else if product == minProduct.Value {
					minProduct.Factorizations = append(minProduct.Factorizations, [2]int{i, j})
				}

				if maxProduct.Value == -1 || product > maxProduct.Value {
					maxProduct.Value = product
					maxProduct.Factorizations = [][2]int{{i, j}}
				} else if product == maxProduct.Value {
					maxProduct.Factorizations = append(maxProduct.Factorizations, [2]int{i, j})
				}
			}
		}
	}

	if minProduct.Value == -1 {
		return Product{}, Product{}, fmt.Errorf("no palindromes found")
	}

	return minProduct, maxProduct, nil
}

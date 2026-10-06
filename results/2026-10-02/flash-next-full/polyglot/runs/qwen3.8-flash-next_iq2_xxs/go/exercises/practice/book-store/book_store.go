package bookstore

import "sort"

func Cost(books []int) int {
	if len(books) == 0 {
		return 0
	}

	// Count occurrences of each book
	counts := make([]int, 5)
	for _, book := range books {
		if book >= 1 && book <= 5 {
			counts[book-1]++
		}
	}

	// Sort counts in descending order
	sort.Sort(sort.Reverse(sort.IntSlice(counts)))

	return calculateCost(counts)
}

func calculateCost(counts []int) int {
	// Remove trailing zeros to find effective number of distinct books
	n := 0
	for _, c := range counts {
		if c > 0 {
			n++
		}
	}

	if n == 0 {
		return 0
	}

	// Try forming a group of size k, where k is the number of distinct books available
	// We want to maximize discount, so we try the largest group first in the greedy approach,
	// but since we are recursive, we can just try all valid group sizes and take the min cost.
	// Actually, the greedy approach of taking the largest possible group is optimal IF we handle the 5+3 vs 4+4 case.
	// Let's use the recursive approach: try all possible group sizes k from 1 to n.
	
	minCost := 0
	// Initialize with a large number
	minCost = 1 << 30

	for k := 1; k <= n; k++ {
		// Create a copy of counts and decrement the top k counts
		newCounts := make([]int, 5)
		copy(newCounts, counts)
		
		for i := 0; i < k; i++ {
			newCounts[i]--
		}
		
		// Calculate cost for this group of size k
		groupCost := groupCost(k)
		
		// Recursively calculate cost for the remaining books
		remainingCost := calculateCost(newCounts)
		
		total := groupCost + remainingCost
		if total < minCost {
			minCost = total
		}
	}

	return minCost
}

func groupCost(n int) int {
	switch n {
	case 1:
		return 800
	case 2:
		return 1520 // 2 * 800 * 0.95
	case 3:
		return 2160 // 3 * 800 * 0.90
	case 4:
		return 2560 // 4 * 800 * 0.80
	case 5:
		return 3200 // 5 * 800 * 0.75
	default:
		return 0
	}
}

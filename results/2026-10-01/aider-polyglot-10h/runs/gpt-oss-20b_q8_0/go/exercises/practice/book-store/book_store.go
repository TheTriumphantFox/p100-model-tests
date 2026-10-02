package bookstore

import "fmt"

// Cost calculates the total price in cents for a list of books.
// Each book costs 800 cents ($8.00). Discounts are applied based on
// the number of distinct titles in a group:
//   2 distinct titles -> 5% discount
//   3 distinct titles -> 10% discount
//   4 distinct titles -> 20% discount
//   5 distinct titles -> 25% discount
//
// The function finds the grouping that yields the maximum discount
// (i.e. the minimum total price).
func Cost(books []int) int {
	// Count how many copies we have of each of the 5 titles.
	// The input slice may contain any integers, but we only care
	// about the first 5 distinct titles. Any value outside 1..5
	// is ignored.
	counts := [5]int{}
	for _, b := range books {
		if b >= 1 && b <= 5 {
			counts[b-1]++
		}
	}

	// Memoization map: key is a string representation of the
	// counts array, value is the minimal cost for that state.
	memo := make(map[string]int)

	// Recursive helper that returns the minimal cost for the
	// current counts state.
	var dfs func([5]int) int
	dfs = func(state [5]int) int {
		// Create a key for memoization.
		key := stateToKey(state)
		if v, ok := memo[key]; ok {
			return v
		}

		// If all counts are zero, no books left.
		if state[0] == 0 && state[1] == 0 && state[2] == 0 && state[3] == 0 && state[4] == 0 {
			memo[key] = 0
			return 0
		}

		// Try all possible group sizes from 1 to 5.
		best := int(^uint(0) >> 1) // Max int
		for groupSize := 1; groupSize <= 5; groupSize++ {
			// Find all combinations of distinct titles that can form a group
			// of this size. We generate indices of titles that have at least
			// one copy left.
			available := []int{}
			for i, c := range state {
				if c > 0 {
					available = append(available, i)
				}
			}
			if len(available) < groupSize {
				continue
			}

			// Generate combinations of available indices of length groupSize.
			combos := combinations(available, groupSize)
			for _, combo := range combos {
				// Build new state after taking one copy of each title in combo.
				newState := state
				for _, idx := range combo {
					newState[idx]--
				}
				// Cost of this group.
				groupCost := groupPrice(groupSize)
				// Total cost for this path.
				total := groupCost + dfs(newState)
				if total < best {
					best = total
				}
			}
		}

		memo[key] = best
		return best
	}

	return dfs(counts)
}

// groupPrice returns the price in cents for a group of distinct books
// of the given size, applying the appropriate discount.
func groupPrice(size int) int {
	base := 800 * size
	switch size {
	case 2:
		return base - base/20 // 5% discount
	case 3:
		return base - base/10 // 10% discount
	case 4:
		return base - base/5  // 20% discount
	case 5:
		return base - base/4  // 25% discount
	default:
		return base // no discount for single book
	}
}

// stateToKey converts a 5-element array into a string key for memoization.
func stateToKey(state [5]int) string {
	// Since the values are small, a simple string concatenation is fine.
	return fmt.Sprintf("%d-%d-%d-%d-%d", state[0], state[1], state[2], state[3], state[4])
}

// combinations returns all combinations of the given slice of ints
// of the specified length. The order of combinations is not important.
func combinations(arr []int, k int) [][]int {
	var res [][]int
	var comb []int
	var dfs func(int)
	dfs = func(start int) {
		if len(comb) == k {
			tmp := make([]int, k)
			copy(tmp, comb)
			res = append(res, tmp)
			return
		}
		for i := start; i < len(arr); i++ {
			comb = append(comb, arr[i])
			dfs(i + 1)
			comb = comb[:len(comb)-1]
		}
	}
	dfs(0)
	return res
}

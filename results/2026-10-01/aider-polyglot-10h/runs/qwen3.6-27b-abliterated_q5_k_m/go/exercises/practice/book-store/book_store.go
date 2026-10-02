package bookstore

func Cost(books []int) int {
	if len(books) == 0 {
		return 0
	}

	// Count occurrences of each book
	counts := make(map[int]int)
	for _, book := range books {
		counts[book]++
	}

	// Group books into sets of distinct titles using a greedy approach
	var groups []int
	for len(counts) > 0 {
		size := 0
		// Iterate over current counts to form a group
		// We need to collect keys to avoid map iteration issues while modifying
		var keys []int
		for k := range counts {
			keys = append(keys, k)
		}

		for _, k := range keys {
			counts[k]--
			size++
			if counts[k] == 0 {
				delete(counts, k)
			}
		}
		groups = append(groups, size)
	}

	// Count groups of size 5 and 3
	count5 := 0
	count3 := 0
	for _, g := range groups {
		if g == 5 {
			count5++
		} else if g == 3 {
			count3++
		}
	}

	// Determine how many (5,3) pairs can be converted to (4,4) pairs
	// Each conversion reduces count5 by 1, count3 by 1, and increases count4 by 2
	pairs := count5
	if count3 < pairs {
		pairs = count3
	}

	// Calculate cost
	totalCost := 0
	for _, g := range groups {
		if g == 5 {
			if pairs > 0 {
				pairs--
				totalCost += 2560 // Cost of group of 4
			} else {
				totalCost += 3000 // Cost of group of 5
			}
		} else if g == 4 {
			totalCost += 2560 // Cost of group of 4
		} else if g == 3 {
			if pairs > 0 {
				pairs--
				totalCost += 2560 // Cost of group of 4
			} else {
				totalCost += 2160 // Cost of group of 3
			}
		} else if g == 2 {
			totalCost += 1520 // Cost of group of 2
		} else if g == 1 {
			totalCost += 800  // Cost of group of 1
		}
	}

	return totalCost
}

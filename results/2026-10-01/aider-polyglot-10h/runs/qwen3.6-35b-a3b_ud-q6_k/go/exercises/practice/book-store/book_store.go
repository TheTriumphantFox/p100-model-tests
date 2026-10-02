package bookstore

func Cost(books []int) int {
	// Count the frequency of each book
	freq := make(map[int]int)
	for _, book := range books {
		freq[book]++
	}

	// Extract frequencies into a slice
	frequencies := make([]int, 0, len(freq))
	for _, count := range freq {
		frequencies = append(frequencies, count)
	}

	// Greedily form groups of distinct books
	groups := make([]int, 0)
	for len(frequencies) > 0 {
		// Count how many distinct books are available
		groupSize := 0
		for _, f := range frequencies {
			if f > 0 {
				groupSize++
			}
		}
		
		groups = append(groups, groupSize)
		
		// Decrease the count of the books used in this group
		newFreqs := make([]int, 0)
		for _, f := range frequencies {
			if f > 0 {
				newFreqs = append(newFreqs, f-1)
			}
		}
		frequencies = newFreqs
	}

	// Optimization: 5+3 is more expensive than 4+4.
	// 5+3 = 3000 + 2160 = 5160
	// 4+4 = 2560 + 2560 = 5120
	// So replace pairs of (5, 3) with (4, 4).
	
	count5 := 0
	count3 := 0
	for _, g := range groups {
		if g == 5 {
			count5++
		} else if g == 3 {
			count3++
		}
	}
	
	replacements := count5
	if count3 < count5 {
		replacements = count3
	}
	
	// Adjust groups: remove 'replacements' 5s and 'replacements' 3s, add 2*replacements 4s
	finalGroups := make([]int, 0)
	for _, g := range groups {
		if g == 5 && replacements > 0 {
			replacements--
		} else if g == 3 && replacements > 0 {
			replacements--
		} else {
			finalGroups = append(finalGroups, g)
		}
	}
	
	// Add the new 4s
	for i := 0; i < count5 - (count5 - replacements); i++ {
		finalGroups = append(finalGroups, 4)
	}
	for i := 0; i < count3 - (count3 - replacements); i++ {
		finalGroups = append(finalGroups, 4)
	}

	totalCost := 0
	for _, g := range finalGroups {
		switch g {
		case 1:
			totalCost += 800
		case 2:
			totalCost += 1520
		case 3:
			totalCost += 2160
		case 4:
			totalCost += 2560
		case 5:
			totalCost += 3000
		}
	}

	return totalCost
}

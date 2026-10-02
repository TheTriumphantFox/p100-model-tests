package bookstore

func Cost(books []int) int {
    // Count occurrences of each book (1-5)
    counts := make([]int, 5)
    for _, book := range books {
        counts[book-1]++
    }

    // We'll use dynamic programming to find the optimal grouping
    // dp[i][j][k][l][m] represents the maximum discount for counts [i,j,k,l,m]
    // But since we only have 5 books, we can use a more efficient representation

    // The maximum count for any book is the total number of books
    maxCount := 0
    for _, c := range counts {
        if c > maxCount {
            maxCount = c
        }
    }

    // Create a DP table where dp[i][j][k][l][m] is the maximum discount
    // We'll use a 5-dimensional array, but in Go we'll flatten it
    dp := make([][][][][]int, counts[0]+1)
    for i := range dp {
        dp[i] = make([][][][]int, counts[1]+1)
        for j := range dp[i] {
            dp[i][j] = make([][][]int, counts[2]+1)
            for k := range dp[i][j] {
                dp[i][j][k] = make([][]int, counts[3]+1)
                for l := range dp[i][j][k] {
                    dp[i][j][k][l] = make([]int, counts[4]+1)
                }
            }
        }
    }

    // Initialize base case (all zeros)
    dp[0][0][0][0][0] = 0

    // Fill the DP table
    for i := 0; i <= counts[0]; i++ {
        for j := 0; j <= counts[1]; j++ {
            for k := 0; k <= counts[2]; k++ {
                for l := 0; l <= counts[3]; l++ {
                    for m := 0; m <= counts[4]; m++ {
                        if i == 0 && j == 0 && k == 0 && l == 0 && m == 0 {
                            continue
                        }

                        // Option 1: Don't form any group with these counts
                        max := i*800 + j*800 + k*800 + l*800 + m*800

                        // Option 2: Try to form a group of 5
                        if i > 0 && j > 0 && k > 0 && l > 0 && m > 0 {
                            prev := dp[i-1][j-1][k-1][l-1][m-1]
                            if prev != 0 {
                                max = min(max, prev + 5*600)
                            }
                        }

                        // Option 3: Try to form a group of 4
                        // Try all combinations of 4 books
                        if i > 0 && j > 0 && k > 0 && l > 0 {
                            prev := dp[i-1][j-1][k-1][l-1][m]
                            if prev != 0 {
                                max = min(max, prev + 4*640)
                            }
                        }
                        if i > 0 && j > 0 && k > 0 && m > 0 {
                            prev := dp[i-1][j-1][k-1][l][m-1]
                            if prev != 0 {
                                max = min(max, prev + 4*640)
                            }
                        }
                        if i > 0 && j > 0 && l > 0 && m > 0 {
                            prev := dp[i-1][j-1][k][l-1][m-1]
                            if prev != 0 {
                                max = min(max, prev + 4*640)
                            }
                        }
                        if i > 0 && k > 0 && l > 0 && m > 0 {
                            prev := dp[i-1][j][k-1][l-1][m-1]
                            if prev != 0 {
                                max = min(max, prev + 4*640)
                            }
                        }
                        if j > 0 && k > 0 && l > 0 && m > 0 {
                            prev := dp[i][j-1][k-1][l-1][m-1]
                            if prev != 0 {
                                max = min(max, prev + 4*640)
                            }
                        }

                        // Option 4: Try to form a group of 3
                        // Try all combinations of 3 books
                        if i > 0 && j > 0 && k > 0 {
                            prev := dp[i-1][j-1][k-1][l][m]
                            if prev != 0 {
                                max = min(max, prev + 3*720)
                            }
                        }
                        if i > 0 && j > 0 && l > 0 {
                            prev := dp[i-1][j-1][k][l-1][m]
                            if prev != 0 {
                                max = min(max, prev + 3*720)
                            }
                        }
                        if i > 0 && j > 0 && m > 0 {
                            prev := dp[i-1][j-1][k][l][m-1]
                            if prev != 0 {
                                max = min(max, prev + 3*720)
                            }
                        }
                        if i > 0 && k > 0 && l > 0 {
                            prev := dp[i-1][j][k-1][l-1][m]
                            if prev != 0 {
                                max = min(max, prev + 3*720)
                            }
                        }
                        if i > 0 && k > 0 && m > 0 {
                            prev := dp[i-1][j][k-1][l][m-1]
                            if prev != 0 {
                                max = min(max, prev + 3*720)
                            }
                        }
                        if i > 0 && l > 0 && m > 0 {
                            prev := dp[i-1][j][k][l-1][m-1]
                            if prev != 0 {
                                max = min(max, prev + 3*720)
                            }
                        }
                        if j > 0 && k > 0 && l > 0 {
                            prev := dp[i][j-1][k-1][l-1][m]
                            if prev != 0 {
                                max = min(max, prev + 3*720)
                            }
                        }
                        if j > 0 && k > 0 && m > 0 {
                            prev := dp[i][j-1][k-1][l][m-1]
                            if prev != 0 {
                                max = min(max, prev + 3*720)
                            }
                        }
                        if j > 0 && l > 0 && m > 0 {
                            prev := dp[i][j-1][k][l-1][m-1]
                            if prev != 0 {
                                max = min(max, prev + 3*720)
                            }
                        }
                        if k > 0 && l > 0 && m > 0 {
                            prev := dp[i][j][k-1][l-1][m-1]
                            if prev != 0 {
                                max = min(max, prev + 3*720)
                            }
                        }

                        // Option 5: Try to form a group of 2
                        // Try all combinations of 2 books
                        if i > 0 && j > 0 {
                            prev := dp[i-1][j-1][k][l][m]
                            if prev != 0 {
                                max = min(max, prev + 2*760)
                            }
                        }
                        if i > 0 && k > 0 {
                            prev := dp[i-1][j][k-1][l][m]
                            if prev != 0 {
                                max = min(max, prev + 2*760)
                            }
                        }
                        if i > 0 && l > 0 {
                            prev := dp[i-1][j][k][l-1][m]
                            if prev != 0 {
                                max = min(max, prev + 2*760)
                            }
                        }
                        if i > 0 && m > 0 {
                            prev := dp[i-1][j][k][l][m-1]
                            if prev != 0 {
                                max = min(max, prev + 2*760)
                            }
                        }
                        if j > 0 && k > 0 {
                            prev := dp[i][j-1][k-1][l][m]
                            if prev != 0 {
                                max = min(max, prev + 2*760)
                            }
                        }
                        if j > 0 && l > 0 {
                            prev := dp[i][j-1][k][l-1][m]
                            if prev != 0 {
                                max = min(max, prev + 2*760)
                            }
                        }
                        if j > 0 && m > 0 {
                            prev := dp[i][j-1][k][l][m-1]
                            if prev != 0 {
                                max = min(max, prev + 2*760)
                            }
                        }
                        if k > 0 && l > 0 {
                            prev := dp[i][j][k-1][l-1][m]
                            if prev != 0 {
                                max = min(max, prev + 2*760)
                            }
                        }
                        if k > 0 && m > 0 {
                            prev := dp[i][j][k-1][l][m-1]
                            if prev != 0 {
                                max = min(max, prev + 2*760)
                            }
                        }
                        if l > 0 && m > 0 {
                            prev := dp[i][j][k][l-1][m-1]
                            if prev != 0 {
                                max = min(max, prev + 2*760)
                            }
                        }

                        dp[i][j][k][l][m] = max
                    }
                }
            }
        }
    }

    return dp[counts[0]][counts[1]][counts[2]][counts[3]][counts[4]]
}

func min(a, b int) int {
    if a < b {
        return a
    }
    return b
}

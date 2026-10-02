package connect

import (
	"errors"
)

func ResultOf(lines []string) (string, error) {
	if len(lines) == 0 {
		return "", nil
	}

	rows := len(lines)
	cols := len(lines[0])

	// Build the board
	board := make([][]byte, rows)
	for i, line := range lines {
		if len(line) != cols {
			return "", errors.New("board rows must have equal length")
		}
		board[i] = []byte(line)
	}

	// Check if O wins (Top to Bottom)
	if hasPath(board, 'O', 0, rows-1) {
		return "O", nil
	}

	// Check if X wins (Left to Right)
	if hasPath(board, 'X', 0, cols-1) {
		return "X", nil
	}

	return "", nil
}

// hasPath checks if there is a path for the given player from startEdge to endEdge.
// startEdge and endEdge are indices:
// For O (Top to Bottom): startEdge=0 (row 0), endEdge=rows-1 (last row)
// For X (Left to Right): startEdge=0 (col 0), endEdge=cols-1 (last col)
// Note: The logic below assumes:
// - If checking vertical connection (O), we start from all cells in row 0 and try to reach any cell in the last row.
// - If checking horizontal connection (X), we start from all cells in col 0 and try to reach any cell in the last col.
func hasPath(board [][]byte, player byte, startEdge, endEdge int) bool {
	rows := len(board)
	cols := len(board[0])

	visited := make([][]bool, rows)
	for i := range visited {
		visited[i] = make([]bool, cols)
	}

	queue := make([][2]int, 0)

	// Initialize queue with starting edge cells
	if startEdge == 0 && endEdge == rows-1 {
		// Vertical check (O)
		for c := 0; c < cols; c++ {
			if board[0][c] == player {
				queue = append(queue, [2]int{0, c})
				visited[0][c] = true
			}
		}
	} else if startEdge == 0 && endEdge == cols-1 {
		// Horizontal check (X)
		for r := 0; r < rows; r++ {
			if board[r][0] == player {
				queue = append(queue, [2]int{r, 0})
				visited[r][0] = true
			}
		}
	} else {
		return false
	}

	// BFS
	for len(queue) > 0 {
		current := queue[0]
		queue = queue[1:]
		r, c := current[0], current[1]

		// Check if we reached the end edge
		if startEdge == 0 && endEdge == rows-1 {
			if r == rows-1 {
				return true
			}
		} else if startEdge == 0 && endEdge == cols-1 {
			if c == cols-1 {
				return true
			}
		}

		// Get neighbors
		neighbors := getNeighbors(r, c, rows, cols)
		for _, n := range neighbors {
			nr, nc := n[0], n[1]
			if !visited[nr][nc] && board[nr][nc] == player {
				visited[nr][nc] = true
				queue = append(queue, [2]int{nr, nc})
			}
		}
	}

	return false
}

func getNeighbors(r, c, rows, cols int) [][2]int {
	// Hex grid neighbors for a rectangular representation
	// Standard Hex board connectivity in a 2D array:
	// (r, c-1), (r, c+1)
	// (r-1, c), (r-1, c+1)
	// (r+1, c), (r+1, c+1)
	
	var neighbors [][2]int
	
	// Left
	if c > 0 {
		neighbors = append(neighbors, [2]int{r, c - 1})
	}
	// Right
	if c < cols-1 {
		neighbors = append(neighbors, [2]int{r, c + 1})
	}
	
	// Top-Left
	if r > 0 {
		neighbors = append(neighbors, [2]int{r - 1, c})
	}
	// Top-Right
	if r > 0 && c < cols-1 {
		neighbors = append(neighbors, [2]int{r - 1, c + 1})
	}
	
	// Bottom-Left
	if r < rows-1 {
		neighbors = append(neighbors, [2]int{r + 1, c})
	}
	// Bottom-Right
	if r < rows-1 && c < cols-1 {
		neighbors = append(neighbors, [2]int{r + 1, c + 1})
	}
	
	return neighbors
}

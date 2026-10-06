package connect

import (
	"errors"
	"strings"
)

// ResultOf takes a board representation as a slice of strings and returns the winner ("X", "O", or "") and an error if any.
func ResultOf(lines []string) (string, error) {
	if len(lines) == 0 {
		return "", errors.New("empty board")
	}

	// Parse the board into a 2D grid
	rows := len(lines)
	if rows == 0 {
		return "", errors.New("empty board")
	}

	// Determine board width from the first line
	width := len(strings.Replace(lines[0], " ", "", -1))
	if width == 0 {
		return "", errors.New("invalid board")
	}

	// Create the board grid
	board := make([][]byte, rows)
	for i, line := range lines {
		// Remove spaces from the line to get the actual board representation
		cleanLine := strings.Replace(line, " ", "", -1)
		if len(cleanLine) != width {
			return "", errors.New("invalid board dimensions")
		}
		board[i] = make([]byte, width)
		for j := 0; j < width; j++ {
			board[i][j] = cleanLine[j]
		}
	}

	// Check if player X has won (connects left to right)
	if checkWinX(board, rows, width) {
		return "X", nil
	}

	// Check if player O has won (connects top to bottom)
	if checkWinO(board, rows, width) {
		return "O", nil
	}

	return "", nil
}

// checkWinX checks if player X has connected from left to right
func checkWinX(board [][]byte, rows, cols int) bool {
	// Create visited matrix
	visited := make([][]bool, rows)
	for i := range visited {
		visited[i] = make([]bool, cols)
	}

	// Start from any 'X' in the leftmost column and try to reach the rightmost column
	for row := 0; row < rows; row++ {
		if board[row][0] == 'X' {
			if dfsX(board, visited, row, 0, rows, cols) {
				return true
			}
		}
	}
	return false
}

// dfsX performs DFS to check if there's a path from (row, col) to the right edge for player X
func dfsX(board [][]byte, visited [][]bool, row, col, rows, cols int) bool {
	// Check bounds and if already visited or not an X
	if row < 0 || row >= rows || col < 0 || col >= cols || visited[row][col] || board[row][col] != 'X' {
		return false
	}

	// Mark as visited
	visited[row][col] = true

	// If we reached the rightmost column, we've won
	if col == cols-1 {
		return true
	}

	// Define the 6 possible neighbors in a hex grid
	// For a parallelogram board with hexagonal fields, the neighbors are:
	// (row-1, col), (row-1, col+1), (row, col-1), (row, col+1), (row+1, col-1), (row+1, col)
	neighbors := [][2]int{
		{row - 1, col},
		{row - 1, col + 1},
		{row, col - 1},
		{row, col + 1},
		{row + 1, col - 1},
		{row + 1, col},
	}

	for _, neighbor := range neighbors {
		nr, nc := neighbor[0], neighbor[1]
		if nr >= 0 && nr < rows && nc >= 0 && nc < cols && !visited[nr][nc] && board[nr][nc] == 'X' {
			if dfsX(board, visited, nr, nc, rows, cols) {
				return true
			}
		}
	}

	return false
}

// checkWinO checks if player O has connected from top to bottom
func checkWinO(board [][]byte, rows, cols int) bool {
	// Create visited matrix
	visited := make([][]bool, rows)
	for i := range visited {
		visited[i] = make([]bool, cols)
	}

	// Start from any 'O' in the top row and try to reach the bottom row
	for col := 0; col < cols; col++ {
		if board[0][col] == 'O' {
			if dfsO(board, visited, 0, col, rows, cols) {
				return true
			}
		}
	}
	return false
}

// dfsO performs DFS to check if there's a path from (row, col) to the bottom edge for player O
func dfsO(board [][]byte, visited [][]bool, row, col, rows, cols int) bool {
	// Check bounds and if already visited or not an O
	if row < 0 || row >= rows || col < 0 || col >= cols || visited[row][col] || board[row][col] != 'O' {
		return false
	}

	// Mark as visited
	visited[row][col] = true

	// If we reached the bottom row, we've won
	if row == rows-1 {
		return true
	}

	// Define the 6 possible neighbors in a hex grid
	neighbors := [][2]int{
		{row - 1, col},
		{row - 1, col + 1},
		{row, col - 1},
		{row, col + 1},
		{row + 1, col - 1},
		{row + 1, col},
	}

	for _, neighbor := range neighbors {
		nr, nc := neighbor[0], neighbor[1]
		if nr >= 0 && nr < rows && nc >= 0 && nc < cols && !visited[nr][nc] && board[nr][nc] == 'O' {
			if dfsO(board, visited, nr, nc, rows, cols) {
				return true
			}
		}
	}

	return false
}

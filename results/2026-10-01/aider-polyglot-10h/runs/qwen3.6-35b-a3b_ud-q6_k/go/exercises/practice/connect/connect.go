package connect

import (
	"errors"
)

func ResultOf(lines []string) (string, error) {
	if len(lines) == 0 {
		return "", errors.New("empty board")
	}

	// Parse the board into a 2D slice of runes, ignoring spaces
	var board [][]rune
	for _, line := range lines {
		var row []rune
		for _, r := range line {
			if r != ' ' {
				row = append(row, r)
			}
		}
		if len(row) > 0 {
			board = append(board, row)
		}
	}

	if len(board) == 0 {
		return "", errors.New("empty board")
	}

	// Check for Player O (Top to Bottom)
	if hasPath(board, 'O', func(r, c int) bool {
		return r == len(board)-1
	}) {
		return "O", nil
	}

	// Check for Player X (Left to Right)
	if hasPath(board, 'X', func(r, c int) bool {
		return c == len(board[r])-1
	}) {
		return "X", nil
	}

	return "", nil
}

// hasPath performs a BFS to see if there is a path from the start side to the target condition.
// For 'O', start side is row 0. Target is any cell in the last row.
// For 'X', start side is col 0. Target is any cell in the last col.
func hasPath(board [][]rune, player rune, isTarget func(r, c int) bool) bool {
	rows := len(board)
	if rows == 0 {
		return false
	}

	// Determine start positions based on player
	var starts []struct{ r, c int }

	if player == 'O' {
		for c := 0; c < len(board[0]); c++ {
			if board[0][c] == 'O' {
				starts = append(starts, struct{ r, c int }{0, c})
			}
		}
	} else if player == 'X' {
		for r := 0; r < rows; r++ {
			if len(board[r]) > 0 && board[r][0] == 'X' {
				starts = append(starts, struct{ r, c int }{r, 0})
			}
		}
	}

	if len(starts) == 0 {
		return false
	}

	visited := make(map[string]bool)
	queue := make([]struct{ r, c int }, 0)

	for _, s := range starts {
		key := fmtKey(s.r, s.c)
		if !visited[key] {
			visited[key] = true
			queue = append(queue, s)
		}
	}

	// Hexagonal neighbors offsets for a skewed grid representation
	// In this representation, row r, col c has neighbors:
	// (r-1, c-1), (r-1, c), (r, c-1), (r, c+1), (r+1, c-1), (r+1, c)
	neighbors := []struct{ dr, dc int }{
		{-1, -1}, {-1, 0},
		{0, -1},  {0, 1},
		{1, -1},  {1, 0},
	}

	for len(queue) > 0 {
		curr := queue[0]
		queue = queue[1:]

		if isTarget(curr.r, curr.c) {
			return true
		}

		for _, n := range neighbors {
			nr, nc := curr.r+n.dr, curr.c+n.dc

			// Check bounds
			if nr < 0 || nr >= rows {
				continue
			}
			if nc < 0 || nc >= len(board[nr]) {
				continue
			}

			key := fmtKey(nr, nc)
			if visited[key] {
				continue
			}

			if board[nr][nc] == player {
				visited[key] = true
				queue = append(queue, struct{ r, c int }{nr, nc})
			}
		}
	}

	return false
}

func fmtKey(r, c int) string {
	return string(rune(r)) + "," + string(rune(c))
}

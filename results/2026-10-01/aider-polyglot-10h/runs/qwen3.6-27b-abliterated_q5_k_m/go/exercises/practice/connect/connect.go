package connect

func ResultOf(lines []string) (string, error) {
	// Parse the board
	board := make([][]byte, len(lines))
	for r, line := range lines {
		row := make([]byte, 0)
		for _, ch := range line {
			if ch != ' ' {
				row = append(row, byte(ch))
			}
		}
		board[r] = row
	}

	// Check for O winning (Top to Bottom)
	if hasPath(board, 'O', func(r, c int) bool { return r == 0 }, func(r, c int) bool { return r == len(board)-1 }) {
		return "O", nil
	}

	// Check for X winning (Left to Right)
	if hasPath(board, 'X', func(r, c int) bool { return c == 0 }, func(r, c int) bool { return c == len(board[r])-1 }) {
		return "X", nil
	}

	return "", nil
}

func hasPath(board [][]byte, player byte, isStart, isEnd func(r, c int) bool) bool {
	if len(board) == 0 {
		return false
	}

	visited := make([][]bool, len(board))
	for r := range visited {
		visited[r] = make([]bool, len(board[r]))
	}

	queue := [][2]int{}

	// Initialize queue with all starting cells
	for r := 0; r < len(board); r++ {
		for c := 0; c < len(board[r]); c++ {
			if board[r][c] == player && isStart(r, c) {
				queue = append(queue, [2]int{r, c})
				visited[r][c] = true
			}
		}
	}

	// Directions for hex grid neighbors
	// (dr, dc)
	dirs := [][2]int{
		{0, -1},  // Left
		{0, 1},   // Right
		{-1, 0},  // Up-Left
		{-1, 1},  // Up-Right
		{1, -1},  // Down-Left
		{1, 0},   // Down-Right
	}

	for len(queue) > 0 {
		curr := queue[0]
		queue = queue[1:]
		r, c := curr[0], curr[1]

		if isEnd(r, c) {
			return true
		}

		for _, d := range dirs {
			nr, nc := r+d[0], c+d[1]
			if nr >= 0 && nr < len(board) && nc >= 0 && nc < len(board[nr]) {
				if !visited[nr][nc] && board[nr][nc] == player {
					visited[nr][nc] = true
					queue = append(queue, [2]int{nr, nc})
				}
			}
		}
	}

	return false
}
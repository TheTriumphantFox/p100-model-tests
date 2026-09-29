def minPath(grid, k):
    N = len(grid)
    # Find position of each value
    pos = {}
    for i in range(N):
        for j in range(N):
            pos[grid[i][j]] = (i, j)
    
    if k == 1:
        return [1]
    
    # Start from the cell with value 1
    current = pos[1]
    path = [1]
    
    for _ in range(k - 1):
        ci, cj = current
        best_val = float('inf')
        best_pos = None
        for di, dj in [(-1,0),(1,0),(0,-1),(0,1)]:
            ni, nj = ci + di, cj + dj
            if 0 <= ni < N and 0 <= nj < N:
                val = grid[ni][nj]
                if val < best_val:
                    best_val = val
                    best_pos = (ni, nj)
        current = best_pos
        path.append(grid[current[0]][current[1]])
    
    return path

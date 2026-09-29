def minPath(grid, k):
    n = len(grid)
    # Find the cell with the minimum value
    min_val = float('inf')
    min_pos = None
    for i in range(n):
        for j in range(n):
            if grid[i][j] < min_val:
                min_val = grid[i][j]
                min_pos = (i, j)
    
    # The minimum path of length k will start at the minimum value cell
    # and then alternate between the minimum value and its smallest neighbor
    # to keep the sequence lexicographically smallest.
    # Actually, we need to find the lexicographically smallest sequence of length k.
    # Since we can revisit cells, the optimal strategy is:
    # 1. Start at the global minimum cell.
    # 2. At each step, move to the smallest possible neighbor (including possibly staying? No, must move to neighbor).
    # But wait, we can revisit cells. So after starting at min, we want the next values to be as small as possible.
    # The smallest possible value we can reach from min_pos is the minimum among its neighbors.
    # Then from there, we can go back to min_pos (which is the global minimum) and so on.
    # So the path will be: [min_val, smallest_neighbor_of_min, min_val, smallest_neighbor_of_min, ...]
    # But we need to be careful: what if there's a path that doesn't start at the global minimum but gives a lexicographically smaller sequence?
    # No, because the first element determines a lot. If we start with a larger value, it's already lexicographically larger.
    # So we must start at the global minimum.
    
    # Now, from the global minimum cell, we want to pick the smallest neighbor to go to.
    # Then from that neighbor, we want to go back to the global minimum (since it's the smallest possible value).
    # So the path will alternate: min_val, smallest_neighbor, min_val, smallest_neighbor, ...
    
    # Find the smallest neighbor of the min_pos
    i, j = min_pos
    neighbors = []
    for di, dj in [(-1,0), (1,0), (0,-1), (0,1)]:
        ni, nj = i + di, j + dj
        if 0 <= ni < n and 0 <= nj < n:
            neighbors.append(grid[ni][nj])
    smallest_neighbor = min(neighbors)
    
    # Build the path
    result = []
    for step in range(k):
        if step % 2 == 0:
            result.append(min_val)
        else:
            result.append(smallest_neighbor)
    
    return result

def minPath(grid, k):
    """
    Given a grid with N rows and N columns (N >= 2) and a positive integer k, 
    each cell of the grid contains a value. Every integer in the range [1, N * N]
    inclusive appears exactly once on the cells of the grid.

    You have to find the minimum path of length k in the grid. You can start
    from any cell, and in each step you can move to any of the neighbor cells,
    in other words, you can go to cells which share an edge with you current
    cell.
    Please note that a path of length k means visiting exactly k cells (not
    necessarily distinct).
    You CANNOT go off the grid.
    A path A (of length k) is considered less than a path B (of length k) if
    after making the ordered lists of the values on the cells that A and B go
    through (let's call them lst_A and lst_B), lst_A is lexicographically less
    than lst_B, in other words, there exist an integer index i (1 <= i <= k)
    such that lst_A[i] < lst_B[i] and for any j (1 <= j < i) we have
    lst_A[j] = lst_B[j].
    It is guaranteed that the answer is unique.
    Return an ordered list of the values on the cells that the minimum path go through.

    Examples:

        Input: grid = [ [1,2,3], [4,5,6], [7,8,9]], k = 3
        Output: [1, 2, 1]

        Input: grid = [ [5,9,3], [4,1,6], [7,8,2]], k = 1
        Output: [1]
    """
    n = len(grid)
    # Find the position of value 1 (the minimum value)
    min_val = 1
    min_r, min_c = -1, -1
    for i in range(n):
        for j in range(n):
            if grid[i][j] == 1:
                min_r, min_c = i, j
                break
        if min_r != -1:
            break
    
    # The minimum path will start with 1, then we want to minimize subsequent values
    # Since we want lexicographically smallest path, we start at the cell with value 1
    # Then at each step, we choose the neighbor with the smallest value
    
    path = [1]
    r, c = min_r, min_c
    
    for _ in range(1, k):
        # Find neighbors and pick the one with minimum value
        min_neighbor_val = float('inf')
        min_neighbor_pos = None
        
        # Check all 4 neighbors
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < n and 0 <= nc < n:
                if grid[nr][nc] < min_neighbor_val:
                    min_neighbor_val = grid[nr][nc]
                    min_neighbor_pos = (nr, nc)
        
        if min_neighbor_pos is not None:
            r, c = min_neighbor_pos
            path.append(min_neighbor_val)
        else:
            # This shouldn't happen for valid grids, but handle edge case
            path.append(grid[r][c])
    
    return path

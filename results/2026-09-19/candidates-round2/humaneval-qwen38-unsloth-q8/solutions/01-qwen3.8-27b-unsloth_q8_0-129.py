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
    
    # Find the position of the minimum value (which is 1)
    # Since we want lexicographically smallest path, we should start from the cell with value 1
    # But wait, we can start from any cell. However, the lexicographically smallest path must start with the smallest possible value.
    # The smallest value in the grid is 1. So the first element of the path must be 1.
    # Then from the cell containing 1, we need to find the next smallest value reachable in one step, and so on.
    
    # Actually, let's think more carefully. We need to find the lexicographically smallest sequence of k values.
    # The first value should be as small as possible. The smallest value in the grid is 1, so the first value must be 1.
    # Then from the cell with value 1, we look at all neighbors and pick the one with the smallest value.
    # Then from that cell, we look at all neighbors and pick the one with the smallest value, etc.
    
    # But wait, is it always optimal to greedily pick the smallest neighbor? Let's think...
    # Since we want lexicographically smallest, at each step we want the smallest possible next value.
    # The choice at step i only affects step i and beyond. To minimize lexicographically, we should minimize step 1 first, then step 2, etc.
    # So yes, greedy should work: at each step, from the current cell, pick the neighbor with the smallest value.
    
    # But wait, what if there are multiple cells with value 1? No, each value appears exactly once.
    
    # Let's find the position of value 1.
    pos = {}
    for i in range(n):
        for j in range(n):
            pos[grid[i][j]] = (i, j)
    
    # Start from the cell with value 1
    current = pos[1]
    path = [1]
    
    for _ in range(k - 1):
        i, j = current
        # Find the neighbor with the smallest value
        min_val = float('inf')
        min_pos = None
        for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            ni, nj = i + di, j + dj
            if 0 <= ni < n and 0 <= nj < n:
                val = grid[ni][nj]
                if val < min_val:
                    min_val = val
                    min_pos = (ni, nj)
        path.append(min_val)
        current = min_pos
    
    return path

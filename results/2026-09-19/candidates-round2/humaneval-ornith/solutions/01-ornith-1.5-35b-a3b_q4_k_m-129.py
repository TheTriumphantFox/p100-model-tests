
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
from collections import deque


def minpath(grid, k):
    """
    Find the lexicographically smallest path of length k in the grid.
    """
    N = len(grid)

    def neighbors(r, c):
        if r > 0:
            yield r - 1, c
        if r + 1 < N:
            yield r + 1, c
        if c > 0:
            yield r, c - 1
        if c + 1 < N:
            yield r, c + 1

    # pos maps a value to its (row, col)
    pos = {}
    for r in range(N):
        for c in range(N):
            pos[grid[r][c]] = (r, c)

    # Start from the smallest value
    best = [pos[1]]
    for _ in range(k - 1):
        nxt = []
        for (r, c) in best:
            for (nr, nc) in neighbors(r, c):
                nxt.append((grid[nr][nc], nr, nc))
        nxt.sort()
        threshold = nxt[0][0]
        best = [(nr, nc) for (_, nr, nc) in nxt if _ == threshold]
    return [grid[r][c] for (r, c) in best]


def minpath(grid, k):
    """
    Find the lexicographically smallest path of length k in the grid.
    """
    N = len(grid)

    def neighbors(r, c):
        if r > 0:
            yield r - 1, c
        if r + 1 < N:
            yield r + 1, c
        if c > 0:
            yield r, c - 1
        if c + 1 < N:
            yield r, c + 1

    # pos maps a value to its (row, col)
    pos = {}
    for r in range(N):
        for c in range(N):
            pos[grid[r][c]] = (r, c)

    # Start from the smallest value
    best = [pos[1]]
    for _ in range(k - 1):
        nxt = []
        for (r, c) in best:
            for (nr, nc) in neighbors(r, c):
                nxt.append((grid[nr][nc], nr, nc))
        nxt.sort()
        threshold = nxt[0][0]
        best = [(nr, nc) for (_, nr, nc) in nxt if _ == threshold]
    return [grid[r][c] for (r, c) in best]

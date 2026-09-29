from heapq import heappop, heappush

def minPath(grid, k):
    n = len(grid)
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    # Priority queue: (current_path, current_value, x, y)
    heap = []
    # Initialize the heap with all possible starting positions
    for i in range(n):
        for j in range(n):
            heappush(heap, ([grid[i][j]], grid[i][j], i, j))

    for _ in range(k - 1):
        current_path, current_value, x, y = heappop(heap)
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < n and 0 <= ny < n:
                new_path = current_path + [grid[nx][ny]]
                heappush(heap, (new_path, grid[nx][ny], nx, ny))

    return heappop(heap)[0]

from typing import List

def minPath(grid: List[List[int]], k: int) -> List[int]:
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
    
    # Directions: up, down, left, right
    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    
    # We use a priority queue (min-heap) to explore paths.
    # Each element is a tuple: (path_value, path_list, current_row, current_col)
    # path_value is the integer value of the last cell in the path.
    # path_list is the list of values visited so far.
    # We use a set to keep track of visited states to avoid cycles.
    # A state is (path_list, current_row, current_col).
    # Since path_list can be long, we use a tuple for hashing.
    
    # Initialize the heap with all possible starting cells.
    heap = []
    visited = set()
    
    for i in range(n):
        for j in range(n):
            val = grid[i][j]
            # The initial path value is the value of the starting cell.
            # The initial path list is just [val].
            heap.append((val, [val], i, j))
            visited.add((tuple([val]), i, j))
    
    # Python's heapq module is a min-heap.
    import heapq
    heapq.heapify(heap)
    
    while heap:
        current_val, path, r, c = heapq.heappop(heap)
        
        # If the path length is k, we have found the minimum path.
        if len(path) == k:
            return path
        
        # Explore neighbors.
        for dr, dc in dirs:
            nr, nc = r + dr, c + dc
            if 0 <= nr < n and 0 <= nc < n:
                new_val = grid[nr][nc]
                new_path = path + [new_val]
                new_state = (tuple(new_path), nr, nc)
                
                if new_state not in visited:
                    visited.add(new_state)
                    heapq.heappush(heap, (new_val, new_path, nr, nc))
    
    # The problem guarantees a solution, so we should never reach here.
    return []

def can_chain(dominoes):
    if not dominoes:
        return []

    # Check if all degrees are even (Eulerian circuit condition)
    degrees = {}
    for a, b in dominoes:
        degrees[a] = degrees.get(a, 0) + 1
        degrees[b] = degrees.get(b, 0) + 1
    
    for count in degrees.values():
        if count % 2 != 0:
            return None

    # Use Hierholzer's algorithm or simple DFS to find the circuit
    # Since the graph is small, a simple backtracking DFS is sufficient.
    
    # Build adjacency list
    adj = {}
    for i, (a, b) in enumerate(dominoes):
        if a not in adj:
            adj[a] = []
        if b not in adj:
            adj[b] = []
        adj[a].append((b, i))
        adj[b].append((a, i))

    used = [False] * len(dominoes)
    path = []

    def dfs(node):
        for neighbor, idx in adj[node]:
            if not used[idx]:
                used[idx] = True
                path.append(dominoes[idx])
                dfs(neighbor)
                # Backtrack if needed, but for Eulerian circuit in connected component
                # we just need to ensure we visit all edges.
                # However, simple DFS might get stuck. 
                # Let's use a standard backtracking approach for clarity and correctness on small inputs.
                path.pop()
                used[idx] = False
                return True
        return False

    # Start from the first domino's first element
    start_node = dominoes[0][0]
    
    # We need to use all dominoes
    # Let's try a more robust backtracking
    
    def solve(current_node, current_chain, remaining):
        if not remaining:
            if current_chain[0][0] == current_node:
                return current_chain
            return None
        
        for i, (a, b) in enumerate(remaining):
            if a == current_node:
                new_remaining = remaining[:i] + remaining[i+1:]
                res = solve(b, current_chain + [(a, b)], new_remaining)
                if res:
                    return res
            if b == current_node:
                new_remaining = remaining[:i] + remaining[i+1:]
                res = solve(a, current_chain + [(b, a)], new_remaining)
                if res:
                    return res
        return None

    result = solve(dominoes[0][0], [], dominoes)
    return result

def can_chain(dominoes):
    if not dominoes:
        return []
    
    if len(dominoes) == 1:
        if dominoes[0][0] == dominoes[0][1]:
            return [dominoes[0]]
        return None

    # Check if Eulerian cycle is possible: all nodes must have even degree
    degrees = {}
    for a, b in dominoes:
        degrees[a] = degrees.get(a, 0) + 1
        degrees[b] = degrees.get(b, 0) + 1
        
    for count in degrees.values():
        if count % 2 != 0:
            return None

    n = len(dominoes)
    used = [False] * n
    
    def backtrack(chain, last_val, start_val):
        if len(chain) == n:
            if chain[-1][1] == start_val:
                return chain
            return None
        
        for i in range(n):
            if not used[i]:
                a, b = dominoes[i]
                if a == last_val:
                    used[i] = True
                    result = backtrack(chain + [(a, b)], b, start_val)
                    if result:
                        return result
                    used[i] = False
                elif b == last_val:
                    used[i] = True
                    result = backtrack(chain + [(b, a)], a, start_val)
                    if result:
                        return result
                    used[i] = False
                    
        return None

    # We can fix the first domino to reduce search space, as any cycle can be rotated
    # to start with any specific edge. We try both orientations of the first domino.
    first = dominoes[0]
    
    # Try orientation 1: (a, b)
    used[0] = True
    result = backtrack([(first[0], first[1])], first[1], first[0])
    if result:
        return result
    used[0] = False
    
    # Try orientation 2: (b, a) - only if a != b to avoid duplicate work
    if first[0] != first[1]:
        used[0] = True
        result = backtrack([(first[1], first[0])], first[0], first[1])
        if result:
            return result
        used[0] = False
        
    return None

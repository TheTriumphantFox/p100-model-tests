def can_chain(dominoes):
    if not dominoes:
        return []
    
    n = len(dominoes)
    
    # If there's only one domino, it must be a double (e.g., [1,1]) to form a valid chain
    if n == 1:
        if dominoes[0][0] == dominoes[0][1]:
            return [dominoes[0]]
        else:
            return None

    # Helper function for backtracking
    def solve(current_chain, remaining_dominoes):
        if not remaining_dominoes:
            # Check if the chain is closed (first and last numbers match)
            if current_chain[0][0] == current_chain[-1][1]:
                return current_chain
            else:
                return None
        
        last_val = current_chain[-1][1]
        
        for i, domino in enumerate(remaining_dominoes):
            left, right = domino
            
            # Try matching left side of domino with right side of last in chain
            if left == last_val:
                # Create new chain and remaining list
                new_chain = current_chain + [domino]
                new_remaining = remaining_dominoes[:i] + remaining_dominoes[i+1:]
                result = solve(new_chain, new_remaining)
                if result is not None:
                    return result
            
            # Try matching right side of domino with right side of last in chain
            # Only if left != right to avoid duplicate work for doubles, 
            # but generally we should try both orientations if they are different.
            # If left == right, the first if block already covered it.
            if right == last_val and left != right:
                new_chain = current_chain + [(right, left)]
                new_remaining = remaining_dominoes[:i] + remaining_dominoes[i+1:]
                result = solve(new_chain, new_remaining)
                if result is not None:
                    return result
                    
        return None

    # Try starting with each domino in each orientation
    # Since the chain is circular, we can fix the first domino to be dominoes[0]
    # and try both orientations. This reduces the search space significantly.
    
    first_domino = dominoes[0]
    other_dominoes = dominoes[1:]
    
    # Try first orientation: [left, right]
    result = solve([first_domino], other_dominoes)
    if result is not None:
        return result
        
    # Try second orientation: [right, left] if different
    if first_domino[0] != first_domino[1]:
        result = solve([(first_domino[1], first_domino[0])], other_dominoes)
        if result is not None:
            return result
            
    return None

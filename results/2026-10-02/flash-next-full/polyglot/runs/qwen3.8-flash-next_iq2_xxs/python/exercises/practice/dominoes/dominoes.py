def can_chain(dominoes):
    if not dominoes:
        return []
    
    # Start with the first domino
    first = dominoes[0]
    remaining = dominoes[1:]
    
    # Try to build a chain starting with the first domino in both orientations
    chain = _build_chain([first], remaining)
    if chain:
        return chain
    
    # Try flipped first domino if different
    if first[0] != first[1]:
        chain = _build_chain([(first[1], first[0])], remaining)
        if chain:
            return chain
            
    return None

def _build_chain(chain, remaining):
    if not remaining:
        # Check if the chain is closed (first matches last)
        if chain[0][0] == chain[-1][1]:
            return chain
        return None
    
    # Try each remaining domino
    for i in range(len(remaining)):
        stone = remaining[i]
        new_remaining = remaining[:i] + remaining[i+1:]
        
        # Try orientation 1: (a, b)
        if chain[-1][1] == stone[0]:
            new_chain = chain + [stone]
            result = _build_chain(new_chain, new_remaining)
            if result:
                return result
        
        # Try orientation 2: (b, a) - only if different from orientation 1
        if stone[0] != stone[1] and chain[-1][1] == stone[1]:
            flipped = (stone[1], stone[0])
            new_chain = chain + [flipped]
            result = _build_chain(new_chain, new_remaining)
            if result:
                return result
            
    return None

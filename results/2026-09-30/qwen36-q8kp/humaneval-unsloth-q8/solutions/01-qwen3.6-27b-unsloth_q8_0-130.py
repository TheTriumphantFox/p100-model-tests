def tri(n):
    """Everyone knows Fibonacci sequence, it was studied deeply by mathematicians in 
    the last couple centuries. However, what people don't know is Tribonacci sequence.
    Tribonacci sequence is defined by the recurrence:
    tri(1) = 3
    tri(n) = 1 + n / 2, if n is even.
    tri(n) =  tri(n - 1) + tri(n - 2) + tri(n + 1), if n is odd.
    For example:
    tri(2) = 1 + (2 / 2) = 2
    tri(4) = 3
    tri(3) = tri(2) + tri(1) + tri(4)
           = 2 + 3 + 3 = 8 
    You are given a non-negative integer number n, you have to a return a list of the 
    first n + 1 numbers of the Tribonacci sequence.
    Examples:
    tri(3) = [1, 3, 2, 8]
    """
    if n < 0:
        return []
    
    # We need to compute tri(0) through tri(n)
    # From the example: tri(3) = [1, 3, 2, 8]
    # So tri(0) = 1, tri(1) = 3, tri(2) = 2, tri(3) = 8
    
    # Let's figure out the base cases and recurrence:
    # tri(0) = 1 (from example)
    # tri(1) = 3 (given)
    # For even n >= 2: tri(n) = 1 + n / 2
    # For odd n >= 3: tri(n) = tri(n-1) + tri(n-2) + tri(n+1)
    
    # The odd case references tri(n+1), which is even, so we can compute even values first.
    
    # Let's build the list iteratively.
    # We need values up to tri(n). But for odd n, we need tri(n+1) which might be beyond n.
    # So we may need to compute up to tri(n+1) if n is odd.
    
    max_needed = n
    if n >= 1 and n % 2 == 1:
        max_needed = n + 1  # because tri(n) for odd n needs tri(n+1)
    
    # Initialize the result list
    result = [0] * (max_needed + 1)
    
    # Base cases
    result[0] = 1
    if max_needed >= 1:
        result[1] = 3
    
    # Compute even indices first (since odd depends on next even)
    # Even indices: 2, 4, 6, ...
    for i in range(2, max_needed + 1, 2):
        result[i] = 1 + i / 2
    
    # Now compute odd indices: 3, 5, 7, ...
    # tri(n) = tri(n-1) + tri(n-2) + tri(n+1) for odd n
    for i in range(3, max_needed + 1, 2):
        result[i] = result[i - 1] + result[i - 2] + result[i + 1]
    
    # Return first n + 1 elements
    return result[:n + 1]

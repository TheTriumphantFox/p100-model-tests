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
    if n == 0:
        return [1]
    
    # We need to compute values up to index n, but odd indices depend on n+1.
    # To handle this, we compute up to n+1 if n is odd.
    limit = n + 1 if n % 2 == 1 else n
    
    # Initialize list with enough space
    res = [0] * (limit + 1)
    res[0] = 1
    res[1] = 3
    
    # Fill even indices
    for i in range(2, limit + 1):
        if i % 2 == 0:
            res[i] = 1 + i // 2
    
    # Fill odd indices (except possibly the last one if it's odd and we don't have i+1)
    for i in range(3, limit + 1):
        if i % 2 == 1:
            res[i] = res[i - 1] + res[i - 2] + res[i + 1]
    
    return res[:n + 1]

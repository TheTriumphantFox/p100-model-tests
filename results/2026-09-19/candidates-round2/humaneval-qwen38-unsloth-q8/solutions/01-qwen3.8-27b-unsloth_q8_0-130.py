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
    
    # We need to compute tri(0) through tri(n)
    # tri(0) is not explicitly defined, but from the example tri(3) = [1, 3, 2, 8]
    # So tri(0) = 1, tri(1) = 3, tri(2) = 2, tri(3) = 8
    
    # Let's figure out the pattern:
    # tri(0) = 1 (from example)
    # tri(1) = 3 (given)
    # tri(2) = 1 + 2/2 = 2 (even)
    # tri(3) = tri(2) + tri(1) + tri(4) = 2 + 3 + 3 = 8 (odd)
    # tri(4) = 1 + 4/2 = 3 (even)
    # tri(5) = tri(4) + tri(3) + tri(6) = 3 + 8 + 4 = 15 (odd)
    # tri(6) = 1 + 6/2 = 4 (even)
    # tri(7) = tri(6) + tri(5) + tri(8) = 4 + 15 + 5 = 24 (odd)
    # tri(8) = 1 + 8/2 = 5 (even)
    
    # So for even n: tri(n) = 1 + n/2
    # For odd n: tri(n) = tri(n-1) + tri(n-2) + tri(n+1)
    # But tri(n+1) for odd n means n+1 is even, so tri(n+1) = 1 + (n+1)/2
    
    # So for odd n: tri(n) = tri(n-1) + tri(n-2) + 1 + (n+1)/2
    
    # Let's build the list iteratively
    result = [0] * (n + 1)
    result[0] = 1
    if n >= 1:
        result[1] = 3
    
    for i in range(2, n + 1):
        if i % 2 == 0:
            result[i] = 1 + i // 2
        else:
            # tri(i) = tri(i-1) + tri(i-2) + tri(i+1)
            # tri(i+1) is even, so tri(i+1) = 1 + (i+1)//2
            result[i] = result[i-1] + result[i-2] + 1 + (i + 1) // 2
    
    return result

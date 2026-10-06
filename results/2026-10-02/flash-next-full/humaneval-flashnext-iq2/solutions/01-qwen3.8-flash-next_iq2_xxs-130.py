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
    if n == 0:
        return [1]
    if n == 1:
        return [1, 3]
    if n == 2:
        return [1, 3, 2]
    if n == 3:
        return [1, 3, 2, 8]
    
    # We need to compute tri(0), tri(1), ..., tri(n)
    # tri(0) = 1 (from the example: tri(3) = [1, 3, 2, 8], so tri(0)=1, tri(1)=3, tri(2)=2, tri(3)=8)
    # tri(1) = 3
    # For even n: tri(n) = 1 + n // 2 (using integer division based on examples)
    # For odd n > 1: tri(n) = tri(n-1) + tri(n-2) + tri(n+1)
    
    # Let's verify with the examples:
    # tri(0) = 1 (given in output list)
    # tri(1) = 3 (given)
    # tri(2) = 1 + 2//2 = 1 + 1 = 2 ✓
    # tri(3) = tri(2) + tri(1) + tri(4)
    # tri(4) = 1 + 4//2 = 1 + 2 = 3 ✓
    # tri(3) = 2 + 3 + 3 = 8 ✓
    
    # For odd n: tri(n) = tri(n-1) + tri(n-2) + tri(n+1)
    # This is a bit tricky because tri(n+1) depends on tri(n), but for odd n, n+1 is even, so tri(n+1) = 1 + (n+1)//2
    
    result = [1]  # tri(0) = 1
    if n >= 1:
        result.append(3)  # tri(1) = 3
    
    for i in range(2, n + 1):
        if i % 2 == 0:
            # Even: tri(i) = 1 + i // 2
            val = 1 + i // 2
            result.append(val)
        else:
            # Odd: tri(i) = tri(i-1) + tri(i-2) + tri(i+1)
            # But tri(i+1) is for index i+1 which we haven't computed yet
            # However, since i is odd, i+1 is even, so tri(i+1) = 1 + (i+1)//2
            tri_i_plus_1 = 1 + (i + 1) // 2
            val = result[i - 1] + result[i - 2] + tri_i_plus_1
            result.append(val)
    
    return result

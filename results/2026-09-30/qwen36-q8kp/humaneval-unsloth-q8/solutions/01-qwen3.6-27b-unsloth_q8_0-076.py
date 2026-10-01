def is_simple_power(x, n):
    """Your task is to write a function that returns true if a number x is a simple
    power of n and false in other cases.
    x is a simple power of n if n**int=x
    For example:
    is_simple_power(1, 4) => true
    is_simple_power(2, 2) => true
    is_simple_power(8, 2) => true
    is_simple_power(3, 2) => false
    is_simple_power(3, 1) => false
    is_simple_power(5, 3) => false
    """
    if n == 0:
        return x == 0 or x == 1
    if n == 1:
        return x == 1
    if n == -1:
        return x == 1 or x == -1
    
    # Check if x is a power of n
    # We need to find if there exists an integer k such that n**k == x
    # Handle negative bases carefully
    
    if x == 1:
        return True  # n**0 = 1 for any n != 0
    
    if x == 0:
        return False  # n**k = 0 has no solution for finite k when n != 0
    
    # For positive n
    if n > 0:
        if x <= 0:
            return False
        # Check powers of n
        power = 1
        while power < x:
            power *= n
        return power == x
    else:
        # n is negative
        # n**k can be positive or negative depending on k
        # If x is positive, k must be even
        # If x is negative, k must be odd
        abs_n = abs(n)
        abs_x = abs(x)
        
        # Check if abs_x is a power of abs_n
        power = 1
        while power < abs_x:
            power *= abs_n
        
        if power != abs_x:
            return False
        
        # Now check sign consistency
        # We need to find if there's an integer k such that n**k == x
        # Since abs(n)**k == abs(x), we just need to check if the sign matches
        # For negative n: n**k has sign (-1)**k
        # So if x > 0, k must be even; if x < 0, k must be odd
        
        # Find k such that abs_n**k == abs_x
        k = 0
        temp = 1
        while temp < abs_x:
            temp *= abs_n
            k += 1
        
        # Check if n**k == x
        return n ** k == x

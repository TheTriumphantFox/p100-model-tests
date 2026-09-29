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
    if n == 1:
        return x == 1
    if n == -1:
        return x == 1 or x == -1
    if x == 1:
        return True
    if x == 0:
        return False
    
    # Try all possible integer exponents
    # We need to find if there exists an integer k such that n**k == x
    # Since x can be negative, we need to handle that
    
    # Start with positive exponents
    power = 1
    k = 0
    while abs(power) < abs(x):
        k += 1
        power = n ** k
        if power == x:
            return True
    
    # Check if we overshot
    if power == x:
        return True
    
    # Also check negative exponents for cases where x is a fraction
    # But since we're dealing with integers, negative exponents would give fractions
    # unless x is 1 or -1, which we already handled
    
    # For negative bases, we also need to check odd/even powers
    # The loop above should handle it since we're checking exact equality
    
    return False

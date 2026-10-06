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
    if n == 0:
        return x == 0 or x == 1
    if n == -1:
        return x == 1 or x == -1
    if n == 0:
        return x == 0 or x == 1
    
    # Handle negative n: n**int can be positive or negative depending on exponent
    # But typically in these problems, we consider positive integers
    # Let's handle edge cases properly
    
    if x == 1:
        return True  # n**0 = 1 for any n != 0
    
    if x == 0:
        return n != 0  # 0 = n**k only if n != 0 and k > 0, but 0 is not a power of n in standard sense unless n=0
    
    if n == 0:
        return x == 0
    
    if n == 1:
        return x == 1
    
    if n == -1:
        return x == 1 or x == -1
    
    # For |n| > 1, check if x is a power of n
    if abs(n) <= 1:
        return x == 1 or (n == 0 and x == 0) or (n == -1 and (x == 1 or x == -1))
    
    # Check if x is a power of n
    if x == 0:
        return False
    
    # Handle negative x with negative n
    if x < 0:
        if n > 0:
            return False
        # n < 0, check if |x| is a power of |n|
        abs_x = abs(x)
        abs_n = abs(n)
        if abs_n <= 1:
            return abs_x == 1
        while abs_x % abs_n == 0:
            abs_x //= abs_n
            if abs_x == 1:
                return True
        return abs_x == 1
    
    # x > 0, n can be positive or negative
    if n < 0:
        abs_n = abs(n)
        if abs_n <= 1:
            return x == 1
        while x % abs_n == 0:
            x //= abs_n
            if x == 1:
                return True
        return x == 1
    
    # n > 1
    if n <= 1:
        return x == 1
    
    while x % n == 0:
        x //= n
        if x == 1:
            return True
    return x == 1

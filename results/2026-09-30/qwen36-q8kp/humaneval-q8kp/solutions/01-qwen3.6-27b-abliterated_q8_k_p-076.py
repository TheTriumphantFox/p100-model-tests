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
    # k can be positive, negative, or zero
    
    # Handle positive and negative bases
    # For simplicity, iterate through a reasonable range of exponents
    
    # First, handle the case where n is positive
    if n > 0:
        # Try positive exponents
        power = 1
        k = 0
        while power < x:
            k += 1
            power *= n
            if power == x:
                return True
            # Avoid infinite loop for n=1 (already handled) and large numbers
            if k > 100:
                break
        if power == x:
            return True
        # Try negative exponents (only if x is not an integer power, but x could be fractional)
        # For negative exponents, n**(-k) = 1/(n**k), so x would need to be a fraction
        # But the problem seems to deal with integers, so let's check if x can be represented as n**k for negative k
        # This means x = 1/(n**k) for some positive k, so x * n**k = 1
        # For integer x, this only works if x = 1 (already handled) or special cases
        # Let's also check negative exponents more carefully
        for k in range(1, 100):
            if n ** k == 1 / x if x != 0 else False:
                return True
            # More precisely: check if x == n**(-k)
            if abs(x - (1.0 / (n ** k))) < 1e-10:
                return True
        return False
    else:
        # n is negative
        # Try positive exponents
        power = 1
        k = 0
        while abs(power) < abs(x) or (abs(power) == abs(x) and power != x):
            k += 1
            power *= n
            if power == x:
                return True
            if k > 100:
                break
        if power == x:
            return True
        # Try negative exponents
        for k in range(1, 100):
            if abs(x - (1.0 / (n ** k))) < 1e-10:
                return True
        return False

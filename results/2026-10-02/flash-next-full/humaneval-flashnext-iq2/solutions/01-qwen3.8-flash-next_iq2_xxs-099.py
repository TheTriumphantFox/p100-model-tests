def closest_integer(value):
    '''
    Create a function that takes a value (string) representing a number
    and returns the closest integer to it. If the number is equidistant
    from two integers, round it away from zero.

    Examples
    >>> closest_integer("10")
    10
    >>> closest_integer("15.3")
    15

    Note:
    Rounding away from zero means that if the given number is equidistant
    from two integers, the one you should return is the one that is the
    farthest from zero. For example closest_integer("14.5") should
    return 15 and closest_integer("-14.5") should return -15.
    '''
    import math
    
    # Convert the string to a float
    num = float(value)
    
    # Use custom rounding that rounds away from zero for .5 cases
    # Python's built-in round() uses banker's rounding (rounds to nearest even),
    # so we need to implement rounding away from zero manually
    
    if num >= 0:
        # For positive numbers, round away from zero means:
        # if fractional part >= 0.5, round up; else round down
        # We can use math.floor(num + 0.5) for positive numbers
        return int(math.floor(num + 0.5))
    else:
        # For negative numbers, round away from zero means:
        # if fractional part <= -0.5 (i.e., abs(frac) >= 0.5), round down (more negative); else round up (less negative)
        # We can use math.ceil(num - 0.5) for negative numbers
        return int(math.ceil(num - 0.5))

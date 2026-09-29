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
    # Convert the string to a float to handle decimal places
    num = float(value)
    
    # Calculate the integer part and the fractional part
    integer_part = int(num)
    fractional_part = abs(num) - integer_part
    
    # Check if the fractional part is exactly 0.5
    if fractional_part == 0.5:
        # Round away from zero
        return integer_part + (1 if num > 0 else -1)
    else:
        # Standard rounding
        return int(num + (0.5 if num >= 0 else -0.5))

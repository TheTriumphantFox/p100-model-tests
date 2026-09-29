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
    num = float(value)
    
    # Get the floor and ceiling
    import math
    floor_val = math.floor(num)
    ceil_val = math.ceil(num)
    
    # If it's already an integer
    if floor_val == ceil_val:
        return floor_val
    
    # Calculate distances
    dist_to_floor = abs(num - floor_val)
    dist_to_ceil = abs(ceil_val - num)
    
    if dist_to_floor < dist_to_ceil:
        return floor_val
    elif dist_to_ceil < dist_to_floor:
        return ceil_val
    else:
        # Equidistant: round away from zero
        if abs(ceil_val) > abs(floor_val):
            return ceil_val
        else:
            return floor_val

def closest_integer(value):
    """
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
    """
    # Convert the string to a float
    num = float(value)

    # Compute the floor and ceiling of the number
    import math
    floor_val = math.floor(num)
    ceil_val = math.ceil(num)

    # If the number is already an integer, return it directly
    if floor_val == ceil_val:
        return int(floor_val)

    # Determine which integer is closer
    # Compute the absolute differences to the floor and ceiling
    diff_floor = abs(num - floor_val)
    diff_ceil = abs(ceil_val - num)

    # If the differences are equal, round away from zero
    if diff_floor == diff_ceil:
        # Choose the integer with the larger absolute value
        if abs(floor_val) > abs(ceil_val):
            return int(floor_val)
        else:
            return int(ceil_val)
    # Otherwise, return the closer integer
    elif diff_floor < diff_ceil:
        return int(floor_val)
    else:
        return int(ceil_val)

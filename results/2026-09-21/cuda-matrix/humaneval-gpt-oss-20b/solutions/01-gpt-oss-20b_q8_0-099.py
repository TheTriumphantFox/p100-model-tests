import math

def closest_integer(value: str) -> int:
    """
    Return the integer closest to the numeric string `value`.
    If the value is exactly halfway between two integers, round away from zero.
    """
    # Convert the string to a float
    num = float(value)

    # Handle the special case of an exact integer
    if num.is_integer():
        return int(num)

    # Compute the floor and ceil of the number
    lower = math.floor(num)
    upper = math.ceil(num)

    # Distances to the two nearest integers
    dist_lower = abs(num - lower)
    dist_upper = abs(upper - num)

    if dist_lower < dist_upper:
        return int(lower)
    if dist_upper < dist_lower:
        return int(upper)

    # Distances are equal: round away from zero
    return int(upper) if num >= 0 else int(lower)

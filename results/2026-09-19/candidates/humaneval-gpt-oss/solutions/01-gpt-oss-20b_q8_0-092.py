def any_int(x, y, z):
    """
    Returns True if one of the numbers is equal to the sum of the other two,
    and all numbers are integers. Otherwise returns False.
    """
    # Check that all inputs are integers
    if not all(isinstance(v, int) for v in (x, y, z)):
        return False

    # Check each possible combination
    return (x == y + z) or (y == x + z) or (z == x + y)

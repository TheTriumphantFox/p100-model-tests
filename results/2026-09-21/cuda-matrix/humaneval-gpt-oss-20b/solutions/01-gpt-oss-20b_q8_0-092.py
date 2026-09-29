def any_int(x, y, z):
    """
    Returns True if one of the numbers is equal to the sum of the other two
    and all numbers are integers. Otherwise returns False.
    """
    # Check that all inputs are integers
    if not (isinstance(x, int) and isinstance(y, int) and isinstance(z, int)):
        return False

    # Check each possible equality
    return (x == y + z) or (y == x + z) or (z == x + y)

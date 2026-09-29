def is_simple_power(x: int, n: int) -> bool:
    """
    Return True if x is a simple power of n, i.e. there exists an integer k such that
    n ** k == x. Otherwise return False.

    Parameters
    ----------
    x : int
        The number to test.
    n : int
        The base.

    Returns
    -------
    bool
        True if x is a power of n, False otherwise.
    """
    # Handle the special case n == 1
    if n == 1:
        return x == 1

    # Negative bases are not considered in this simple implementation.
    # For negative n, powers alternate sign; we only support positive n.
    if n <= 0:
        return False

    # 1 is always a power (n**0)
    if x == 1:
        return True

    # If x is less than n, it cannot be a positive power of n
    if x < n:
        return False

    # Repeatedly divide x by n while it is divisible.
    while x % n == 0:
        x //= n

    # If we have reduced x to 1, it was a power of n.
    return x == 1

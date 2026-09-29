def largest_divisor(n: int) -> int:
    """
    For a given number n, find the largest number that divides n evenly,
    smaller than n.

    Parameters
    ----------
    n : int
        The number to find the largest proper divisor of.

    Returns
    -------
    int
        The largest divisor of n that is strictly less than n.
        If n <= 1, returns 1.

    Examples
    --------
    >>> largest_divisor(15)
    5
    >>> largest_divisor(28)
    14
    >>> largest_divisor(2)
    1
    >>> largest_divisor(1)
    1
    """
    if n <= 1:
        return 1

    # Check divisors from n-1 down to 1
    for d in range(n - 1, 0, -1):
        if n % d == 0:
            return d

    # Fallback (should never reach here for n > 1)
    return 1

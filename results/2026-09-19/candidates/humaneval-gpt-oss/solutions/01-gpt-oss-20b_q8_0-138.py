def is_equal_to_sum_even(n: int) -> bool:
    """
    Evaluate whether the given number n can be written as the sum of exactly 4 positive even numbers.

    Parameters
    ----------
    n : int
        The number to evaluate.

    Returns
    -------
    bool
        True if n can be expressed as the sum of exactly four positive even integers,
        False otherwise.

    Examples
    --------
    >>> is_equal_to_sum_even(4)
    False
    >>> is_equal_to_sum_even(6)
    False
    >>> is_equal_to_sum_even(8)
    True
    >>> is_equal_to_sum_even(10)
    True
    >>> is_equal_to_sum_even(11)
    False
    """
    # The smallest sum of four positive even numbers is 2+2+2+2 = 8.
    # Any even number >= 8 can be represented as 2 + 2 + 2 + (n-6),
    # where n-6 is also a positive even number.
    return isinstance(n, int) and n >= 8 and n % 2 == 0

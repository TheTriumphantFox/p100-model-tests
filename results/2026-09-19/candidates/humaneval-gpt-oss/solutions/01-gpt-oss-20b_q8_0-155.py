def even_odd_count(num):
    """
    Given an integer, return a tuple that has the number of even and odd digits respectively.

    Parameters
    ----------
    num : int
        The integer to analyze.

    Returns
    -------
    tuple[int, int]
        A tuple (even_count, odd_count).

    Examples
    --------
    >>> even_odd_count(-12)
    (1, 1)
    >>> even_odd_count(123)
    (1, 2)
    >>> even_odd_count(0)
    (1, 0)
    """
    # Work with the absolute value to ignore the sign.
    n = abs(num)

    # Convert to string to iterate over each digit.
    s = str(n)

    even_count = 0
    odd_count = 0

    for ch in s:
        digit = int(ch)
        if digit % 2 == 0:
            even_count += 1
        else:
            odd_count += 1

    return even_count, odd_count

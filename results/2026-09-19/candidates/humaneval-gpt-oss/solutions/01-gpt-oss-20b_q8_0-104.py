def unique_digits(x):
    """
    Given a list of positive integers x, return a sorted list of all
    elements that have no even digit.

    Parameters
    ----------
    x : list[int]
        List of positive integers.

    Returns
    -------
    list[int]
        Sorted list of integers from x that contain only odd digits.

    Examples
    --------
    >>> unique_digits([15, 33, 1422, 1])
    [1, 15, 33]
    >>> unique_digits([152, 323, 1422, 10])
    []
    """
    def has_only_odd_digits(n: int) -> bool:
        """Return True if all digits of n are odd."""
        while n:
            digit = n % 10
            if digit % 2 == 0:  # even digit found
                return False
            n //= 10
        return True

    result = [num for num in x if has_only_odd_digits(num)]
    return sorted(result)

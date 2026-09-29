def order_by_points(nums):
    """
    Sort the given list of integers in ascending order according to the sum of their digits.
    If two numbers have the same digit sum, their relative order from the original list is preserved.

    Parameters
    ----------
    nums : list[int]
        List of integers to sort.

    Returns
    -------
    list[int]
        Sorted list according to the rules described.

    Examples
    --------
    >>> order_by_points([1, 11, -1, -11, -12])
    [-1, -11, 1, -12, 11]
    >>> order_by_points([])
    []
    """
    def digit_sum(n: int) -> int:
        """Return the sum of the absolute value's digits."""
        return sum(int(d) for d in str(abs(n)))

    # Enumerate to keep original indices for stable sorting
    indexed = list(enumerate(nums))
    # Sort by digit sum first, then by original index
    indexed.sort(key=lambda x: (digit_sum(x[1]), x[0]))
    # Extract sorted values
    return [value for _, value in indexed]

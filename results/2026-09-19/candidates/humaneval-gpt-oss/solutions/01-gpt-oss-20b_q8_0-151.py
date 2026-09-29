def double_the_difference(lst):
    """
    Return the sum of squares of the odd integers in ``lst``.
    Negative numbers and non‑integers are ignored.
    If the list is empty, return 0.
    """
    total = 0
    for x in lst:
        # Only consider positive integers that are odd
        if isinstance(x, int) and x >= 0 and x % 2 == 1:
            total += x * x
    return total

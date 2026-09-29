def largest_smallest_integers(lst):
    """
    Returns a tuple (a, b) where:
    - a is the largest negative integer in the list (or None if none exist)
    - b is the smallest positive integer in the list (or None if none exist)

    Examples:
    >>> largest_smallest_integers([2, 4, 1, 3, 5, 7])
    (None, 1)
    >>> largest_smallest_integers([])
    (None, None)
    >>> largest_smallest_integers([0])
    (None, None)
    """
    max_neg = None
    min_pos = None

    for num in lst:
        if num < 0:
            if max_neg is None or num > max_neg:
                max_neg = num
        elif num > 0:
            if min_pos is None or num < min_pos:
                min_pos = num

    return (max_neg, min_pos)

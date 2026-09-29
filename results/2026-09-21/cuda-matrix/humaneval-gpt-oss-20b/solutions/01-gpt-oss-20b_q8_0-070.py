def strange_sort_list(lst):
    """
    Given a list of integers, return a new list sorted in a "strange" order:
    start with the minimum value, then the maximum of the remaining values,
    then the next minimum, then the next maximum, and so on.

    Parameters
    ----------
    lst : list[int]
        The list of integers to sort.

    Returns
    -------
    list[int]
        The list sorted in the strange order.

    Examples
    --------
    >>> strange_sort_list([1, 2, 3, 4])
    [1, 4, 2, 3]
    >>> strange_sort_list([5, 5, 5, 5])
    [5, 5, 5, 5]
    >>> strange_sort_list([])
    []
    """
    # Work on a copy to avoid mutating the input list
    remaining = sorted(lst)
    result = []

    # Alternate between taking the smallest and largest remaining elements
    take_min = True
    while remaining:
        if take_min:
            result.append(remaining.pop(0))
        else:
            result.append(remaining.pop(-1))
        take_min = not take_min

    return result

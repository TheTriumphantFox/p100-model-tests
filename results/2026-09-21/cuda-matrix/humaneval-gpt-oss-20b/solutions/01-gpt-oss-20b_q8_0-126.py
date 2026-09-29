def is_sorted(lst):
    """
    Return True if the list is sorted in ascending order and no number
    appears more than twice. Otherwise return False.
    """
    if not lst:
        return True

    # Check ascending order
    for i in range(len(lst) - 1):
        if lst[i] > lst[i + 1]:
            return False

    # Count occurrences
    counts = {}
    for num in lst:
        counts[num] = counts.get(num, 0) + 1
        if counts[num] > 2:
            return False

    return True

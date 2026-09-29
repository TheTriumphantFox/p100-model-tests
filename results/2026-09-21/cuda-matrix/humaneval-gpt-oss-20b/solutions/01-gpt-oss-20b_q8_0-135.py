def can_arrange(arr):
    """
    Return the largest index i such that arr[i] < arr[i-1].
    If no such index exists, return -1.
    The array contains no duplicate values.
    """
    # Need at least two elements to compare
    if len(arr) < 2:
        return -1

    # Scan from the end to find the largest index satisfying the condition
    for i in range(len(arr) - 1, 0, -1):
        if arr[i] < arr[i - 1]:
            return i
    return -1

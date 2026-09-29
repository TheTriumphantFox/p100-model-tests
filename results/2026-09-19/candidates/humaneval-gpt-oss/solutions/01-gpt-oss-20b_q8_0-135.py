def can_arrange(arr):
    """
    Return the largest index i such that arr[i] < arr[i-1].
    If no such index exists, return -1.
    The array contains no duplicate values.
    """
    for i in range(len(arr) - 1, 0, -1):
        if arr[i] < arr[i - 1]:
            return i
    return -1

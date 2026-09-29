def maximum(arr, k):
    """
    Return a sorted list of length k containing the maximum k numbers from arr.
    """
    if k == 0:
        return []
    # Sort the array in ascending order
    sorted_arr = sorted(arr)
    # Take the last k elements (the largest ones)
    largest_k = sorted_arr[-k:]
    # Return them sorted in ascending order
    return sorted(largest_k)

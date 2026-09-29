def move_one_ball(arr):
    """
    Return True if the array can be sorted in non‑decreasing order by a
    sequence of right shift operations (cyclic rotations).  The array
    contains unique elements.  An empty array is considered sorted.
    """
    if not arr:
        return True

    n = len(arr)
    # The sorted version of the array
    sorted_arr = sorted(arr)

    # Find the index of the smallest element in the original array.
    # That index is the point where a rotation would bring the array
    # into sorted order if possible.
    min_index = arr.index(min(arr))

    # Build the array that would result from rotating the original
    # array left by min_index positions (which is equivalent to
    # rotating right by n - min_index positions).
    rotated = arr[min_index:] + arr[:min_index]

    return rotated == sorted_arr

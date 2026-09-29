def move_one_ball(arr):
    """
    Determine if the given array can be sorted in non-decreasing order by
    performing any number of right shift operations.

    A right shift moves every element one position to the right, with the last
    element wrapping around to the front. The array has unique elements.

    Parameters
    ----------
    arr : list[int]
        The input array.

    Returns
    -------
    bool
        True if the array can be sorted by right shifts, False otherwise.
        An empty array returns True.
    """
    n = len(arr)
    if n <= 1:
        return True

    # Count the number of places where the order breaks (arr[i] > arr[i+1])
    drops = 0
    for i in range(n - 1):
        if arr[i] > arr[i + 1]:
            drops += 1

    # For a circularly sorted (non‑decreasing) array there can be at most one drop.
    # Additionally, the last element must be <= the first element to allow a single rotation.
    if drops == 0:
        return True
    if drops == 1 and arr[-1] <= arr[0]:
        return True
    return False

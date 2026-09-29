def monotonic(l: list) -> bool:
    """Return True if list elements are monotonically increasing or decreasing.

    A list is considered monotonic if it is either non‑decreasing or non‑increasing.
    Empty lists and single‑element lists are trivially monotonic.

    >>> monotonic([1, 2, 4, 20])
    True
    >>> monotonic([1, 20, 4, 10])
    False
    >>> monotonic([4, 1, 0, -10])
    True
    """
    if len(l) <= 1:
        return True

    # Determine the direction of the first non‑zero difference
    direction = 0  # 0 = unknown, 1 = increasing, -1 = decreasing
    for i in range(1, len(l)):
        diff = l[i] - l[i - 1]
        if diff > 0:
            if direction == -1:
                return False
            direction = 1
        elif diff < 0:
            if direction == 1:
                return False
            direction = -1
        # diff == 0: no change, continue

    return True

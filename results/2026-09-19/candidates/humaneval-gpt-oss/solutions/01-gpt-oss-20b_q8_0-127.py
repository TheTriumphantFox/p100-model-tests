def intersection(interval1, interval2):
    """Return "YES" if the length of the intersection of two closed integer intervals
    is a prime number, otherwise return "NO". If the intervals do not intersect,
    return "NO".

    Parameters
    ----------
    interval1 : tuple[int, int]
        The first interval (start, end) with start <= end.
    interval2 : tuple[int, int]
        The second interval (start, end) with start <= end.

    Returns
    -------
    str
        "YES" if the intersection length is prime, otherwise "NO".
    """
    a_start, a_end = interval1
    b_start, b_end = interval2

    # Compute intersection bounds
    inter_start = max(a_start, b_start)
    inter_end = min(a_end, b_end)

    # No intersection
    if inter_start > inter_end:
        return "NO"

    # Length of intersection (closed interval)
    length = inter_end - inter_start + 1

    # Helper to check primality
    def is_prime(n: int) -> bool:
        if n < 2:
            return False
        if n == 2:
            return True
        if n % 2 == 0:
            return False
        i = 3
        while i * i <= n:
            if n % i == 0:
                return False
            i += 2
        return True

    return "YES" if is_prime(length) else "NO"

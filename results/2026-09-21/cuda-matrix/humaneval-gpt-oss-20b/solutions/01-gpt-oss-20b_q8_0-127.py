def intersection(interval1, interval2):
    """Return "YES" if the length of the intersection of two closed intervals is a prime number,
    otherwise return "NO". If the intervals do not intersect, return "NO".
    """
    a_start, a_end = interval1
    b_start, b_end = interval2

    # Compute intersection bounds
    start = max(a_start, b_start)
    end = min(a_end, b_end)

    # No intersection
    if start > end:
        return "NO"

    # Length of intersection (closed interval)
    length = end - start + 1

    # Check if length is prime
    if length < 2:
        return "NO"
    if length == 2:
        return "YES"
    if length % 2 == 0:
        return "NO"

    # Check odd divisors up to sqrt(length)
    i = 3
    while i * i <= length:
        if length % i == 0:
            return "NO"
        i += 2
    return "YES"

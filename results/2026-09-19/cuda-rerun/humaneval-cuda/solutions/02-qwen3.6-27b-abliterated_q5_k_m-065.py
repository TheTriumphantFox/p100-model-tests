def circular_shift(x, shift):
    """Circular shift the digits of the integer x, shift the digits right by shift
    and return the result as a string.
    If shift > number of digits, return digits reversed.
    >>> circular_shift(12, 1)
    "21"
    >>> circular_shift(12, 2)
    "12"
    """
    s = str(x)
    n = len(s)
    if shift > n:
        return s[::-1]
    else:
        # Right circular shift by shift positions
        # The last 'shift' digits move to the front
        shifted = s[-shift:] + s[:-shift] if shift > 0 else s
        return shifted

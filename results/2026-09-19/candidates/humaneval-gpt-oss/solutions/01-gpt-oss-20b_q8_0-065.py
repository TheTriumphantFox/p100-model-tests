def circular_shift(x, shift):
    """Circular shift the digits of the integer x, shift the digits right by shift
    and return the result as a string.
    If shift > number of digits, return digits reversed.
    >>> circular_shift(12, 1)
    "21"
    >>> circular_shift(12, 2)
    "12"
    """
    # Convert the integer to its absolute string representation
    s = str(abs(x))
    n = len(s)

    # If shift is greater than the number of digits, reverse the string
    if shift > n:
        return s[::-1]

    # If shift is zero or equal to the number of digits, return the original string
    if shift == 0 or shift == n:
        return s

    # Perform a right circular shift by taking the last `shift` characters
    # and placing them in front of the remaining part
    return s[-shift:] + s[:-shift]

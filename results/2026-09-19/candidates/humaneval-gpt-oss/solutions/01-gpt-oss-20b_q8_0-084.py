def solve(N: int) -> str:
    """
    Given a positive integer N, return the total sum of its decimal digits
    expressed as a binary string.

    Examples
    --------
    >>> solve(1000)
    '1'
    >>> solve(150)
    '110'
    >>> solve(147)
    '1100'
    >>> solve(0)
    '0'
    """
    # Sum the decimal digits of N
    digit_sum = sum(int(d) for d in str(N))
    # Convert the sum to binary string without the '0b' prefix
    return bin(digit_sum)[2:]

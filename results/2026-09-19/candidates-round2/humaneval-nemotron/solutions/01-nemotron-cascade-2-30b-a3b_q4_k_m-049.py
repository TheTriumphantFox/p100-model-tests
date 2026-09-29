def modp(n: int, p: int) -> int:
    """Return 2**n modulo p (be aware of numerics).

    >>> modp(3, 5)
    3
    >>> modp(1101, 101)
    2
    >>> modp(0, 101)
    1
    >>> modp(3, 11)
    8
    >>> modp(100, 101)
    1
    """
    if p == 1:
        return 0
    result = 1
    base = 2 % p
    exp = n
    while exp > 0:
        if exp & 1:
            result = (result * base) % p
        base = (base * base) % p
        exp >>= 1
    return result

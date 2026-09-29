def fib4(n: int) -> int:
    """
    Compute the n-th element of the fib4 sequence.

    The sequence is defined as:
        fib4(0) = 0
        fib4(1) = 0
        fib4(2) = 2
        fib4(3) = 0
        fib4(n) = fib4(n-1) + fib4(n-2) + fib4(n-3) + fib4(n-4)  for n >= 4

    Parameters
    ----------
    n : int
        The index of the element to compute. Must be non‑negative.

    Returns
    -------
    int
        The n-th fib4 number.

    Examples
    --------
    >>> fib4(5)
    4
    >>> fib4(6)
    8
    >>> fib4(7)
    14
    """
    if n < 0:
        raise ValueError("n must be non‑negative")

    # Base cases
    base = [0, 0, 2, 0]
    if n < 4:
        return base[n]

    # Use a sliding window of the last four values
    a, b, c, d = base  # a=fib4(n-4), b=fib4(n-3), c=fib4(n-2), d=fib4(n-1)
    for _ in range(4, n + 1):
        e = a + b + c + d  # fib4(n)
        a, b, c, d = b, c, d, e
    return d

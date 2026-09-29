def fib4(n: int) -> int:
    """Return the n-th element of the Fib4 sequence.

    The sequence is defined as:
        fib4(0) = 0
        fib4(1) = 0
        fib4(2) = 2
        fib4(3) = 0
        fib4(n) = fib4(n-1) + fib4(n-2) + fib4(n-3) + fib4(n-4)  for n >= 4

    The implementation uses an iterative approach with O(1) extra space
    and O(n) time, avoiding recursion as required.
    """
    if n < 0:
        raise ValueError("n must be a non‑negative integer")

    # Base cases
    if n == 0 or n == 1:
        return 0
    if n == 2:
        return 2
    if n == 3:
        return 0

    # Keep the last four values: fib4(i-4), fib4(i-3), fib4(i-2), fib4(i-1)
    a, b, c, d = 0, 0, 2, 0  # corresponds to fib4(0), fib4(1), fib4(2), fib4(3)

    for i in range(4, n + 1):
        # Compute the next term
        nxt = a + b + c + d
        # Shift the window forward
        a, b, c, d = b, c, d, nxt

    return d

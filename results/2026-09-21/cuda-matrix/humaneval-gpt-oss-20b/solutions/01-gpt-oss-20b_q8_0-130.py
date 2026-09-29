def tri(n: int) -> list[int]:
    """
    Return the first n + 1 numbers of the Tribonacci sequence defined by:
        tri(0) = 1
        tri(1) = 3
        tri(n) = 1 + n // 2          if n is even
        tri(n) = tri(n-1) + tri(n-2) + (1 + (n+1)//2)   if n is odd
    """
    if n < 0:
        raise ValueError("n must be non‑negative")
    seq = [0] * (n + 1)
    seq[0] = 1
    if n >= 1:
        seq[1] = 3
    for i in range(2, n + 1):
        if i % 2 == 0:  # even
            seq[i] = 1 + i // 2
        else:  # odd
            seq[i] = seq[i - 1] + seq[i - 2] + (1 + (i + 1) // 2)
    return seq

def count_up_to(n):
    """Return a list of all prime numbers less than n.

    Parameters
    ----------
    n : int
        Non‑negative integer.  If n <= 2, the result is an empty list.

    Returns
    -------
    list[int]
        All primes p such that 2 <= p < n, in ascending order.
    """
    if n <= 2:
        return []

    # Sieve of Eratosthenes up to n-1
    sieve = [True] * n
    sieve[0:2] = [False, False]  # 0 and 1 are not prime

    for i in range(2, int(n**0.5) + 1):
        if sieve[i]:
            step = i
            start = i * i
            sieve[start:n:step] = [False] * ((n - start - 1) // step + 1)

    return [i for i, is_prime in enumerate(sieve) if is_prime]

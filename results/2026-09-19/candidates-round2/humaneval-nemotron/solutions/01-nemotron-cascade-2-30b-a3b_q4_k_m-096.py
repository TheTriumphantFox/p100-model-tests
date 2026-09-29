def count_up_to(n):
    """Return a list of all prime numbers less than n.

    Args:
        n (int): A non‑negative integer.

    Returns:
        list[int]: A list containing the prime numbers that are < n, in ascending order.
    """
    if n <= 2:
        return []

    # Sieve of Eratosthenes up to n-1
    limit = n - 1
    sieve = [True] * (limit + 1)
    sieve[0] = sieve[1] = False

    for p in range(2, int(limit ** 0.5) + 1):
        if sieve[p]:
            for multiple in range(p * p, limit + 1, p):
                sieve[multiple] = False

    return [i for i, is_prime in enumerate(sieve) if is_prime]

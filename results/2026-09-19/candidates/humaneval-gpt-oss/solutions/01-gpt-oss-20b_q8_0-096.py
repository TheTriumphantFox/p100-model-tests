def count_up_to(n: int) -> list[int]:
    """
    Return a list of all prime numbers less than n.
    """
    if n <= 2:
        return []

    # Sieve of Eratosthenes up to n-1
    sieve = [True] * n
    sieve[0:2] = [False, False]  # 0 and 1 are not prime

    for p in range(2, int(n**0.5) + 1):
        if sieve[p]:
            step = p
            start = p * p
            sieve[start:n:step] = [False] * ((n - start - 1) // step + 1)

    return [i for i, is_prime in enumerate(sieve) if is_prime]

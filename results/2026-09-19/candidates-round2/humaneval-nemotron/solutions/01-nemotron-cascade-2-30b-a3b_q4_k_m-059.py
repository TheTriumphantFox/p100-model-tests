def largest_prime_factor(n: int) -> int:
    """Return the largest prime factor of n. Assume n > 1 and is not a prime.

    >>> largest_prime_factor(13195)
    29
    >>> largest_prime_factor(2048)
    2
    """
    # Remove factors of 2 first
    while n % 2 == 0:
        last_factor = 2
        n //= 2

    # n must be odd at this point, so we can skip even numbers
    factor = 3
    max_factor = 0
    while n > 1:
        while n % factor == 0:
            max_factor = factor
            n //= factor
        factor += 2  # only odd numbers

    # If n is still greater than 2, then n itself is a prime factor
    if n > 2:
        max_factor = n

    return max_factor

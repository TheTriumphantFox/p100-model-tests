def largest_prime_factor(n: int):
    """Return the largest prime factor of n. Assume n > 1 and is not a prime.
    >>> largest_prime_factor(13195)
    29
    >>> largest_prime_factor(2048)
    2
    """
    largest_prime = -1

    # Divide by 2 until n is odd
    while n % 2 == 0:
        largest_prime = 2
        n = n // 2

    # Check for odd divisors up to sqrt(n)
    i = 3
    max_factor = int(n**0.5) + 1
    while i <= max_factor:
        while n % i == 0:
            largest_prime = i
            n = n // i
            max_factor = int(n**0.5) + 1
        i += 2

    if n > 2:
        largest_prime = n

    return largest_prime

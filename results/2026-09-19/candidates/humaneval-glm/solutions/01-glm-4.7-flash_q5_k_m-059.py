def largest_prime_factor(n: int):
    """Return the largest prime factor of n. Assume n > 1 and is not a prime.
    >>> largest_prime_factor(13195)
    29
    >>> largest_prime_factor(2048)
    2
    """
    # Remove all factors of 2 first to handle even numbers efficiently
    while n % 2 == 0:
        n //= 2
    
    # Now n must be odd. We only need to check odd factors up to sqrt(n).
    # If n is a prime > 2, it will remain after the loop.
    i = 3
    max_factor = 1
    while i * i <= n:
        while n % i == 0:
            max_factor = i
            n //= i
        i += 2
    
    # If n is still greater than 2, it is a prime factor larger than sqrt(original n)
    if n > 2:
        return n
    
    return max_factor

def is_multiply_prime(a: int) -> bool:
    """
    Return True if the given number a (< 100) can be expressed as the product of
    exactly three prime numbers (not necessarily distinct), otherwise False.
    """
    if a < 2:
        return False

    # Helper to check primality
    def is_prime(n: int) -> bool:
        if n < 2:
            return False
        if n == 2:
            return True
        if n % 2 == 0:
            return False
        i = 3
        while i * i <= n:
            if n % i == 0:
                return False
            i += 2
        return True

    # Count prime factors (with multiplicity)
    count = 0
    n = a
    for p in range(2, int(n ** 0.5) + 1):
        while n % p == 0:
            if not is_prime(p):
                return False
            count += 1
            n //= p
            if count > 3:
                return False
    # If remaining n > 1, it's a prime factor
    if n > 1:
        if not is_prime(n):
            return False
        count += 1

    return count == 3

from typing import List
import math

def factorize(n: int) -> List[int]:
    """Return list of prime factors of given integer in ascending order.
    Each factor appears as many times as its multiplicity in the prime factorization.
    The product of the returned factors equals the original number.
    """
    if n <= 1:
        return []

    factors: List[int] = []

    # Handle factor 2 separately to allow increment by 2 later
    while n % 2 == 0:
        factors.append(2)
        n //= 2

    # Check odd factors up to sqrt(n)
    limit = int(math.isqrt(n)) + 1
    f = 3
    while f <= limit and n > 1:
        while n % f == 0:
            factors.append(f)
            n //= f
            limit = int(math.isqrt(n)) + 1
        f += 2

    # If remaining n is a prime > 1
    if n > 1:
        factors.append(n)

    return factors

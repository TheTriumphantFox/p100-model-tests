from typing import List


def factorize(n: int) -> List[int]:
    """ Return list of prime factors of given integer in the order from smallest to largest.
    Each of the factors should be listed number of times corresponding to how many times it appeares in factorization.
    Input number should be equal to the product of all factors
    >>> factorize(8)
    [2, 2, 2]
    >>> factorize(25)
    [5, 5]
    >>> factorize(70)
    [2, 5, 7]
    """
    factors: List[int] = []
    # Handle factor 2 separately to allow incrementing by 2 later
    while n % 2 == 0:
        factors.append(2)
        n //= 2

    # Check odd factors from 3 upwards
    divisor = 3
    while divisor * divisor <= n:
        while n % divisor == 0:
            factors.append(divisor)
            n //= divisor
        divisor += 2

    # If n is still greater than 1, it is a prime factor
    if n > 1:
        factors.append(n)

    return factors

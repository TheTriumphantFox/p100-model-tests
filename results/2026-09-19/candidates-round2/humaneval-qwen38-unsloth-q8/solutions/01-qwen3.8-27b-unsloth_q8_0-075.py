def is_multiply_prime(a):
    """Write a function that returns true if the given number is the multiplication of 3 prime numbers
    and false otherwise.
    Knowing that (a) is less then 100. 
    Example:
    is_multiply_prime(30) == True
    30 = 2 * 3 * 5
    """
    def is_prime(n):
        if n < 2:
            return False
        if n == 2:
            return True
        if n % 2 == 0:
            return False
        for i in range(3, int(n**0.5) + 1, 2):
            if n % i == 0:
                return False
        return True
    
    # We need to check if a can be expressed as the product of exactly 3 primes
    # (not necessarily distinct)
    # Since a < 100, we can brute force
    for i in range(2, a + 1):
        if a % i == 0:
            if is_prime(i):
                remaining = a // i
                # Now check if remaining is the product of 2 primes
                for j in range(2, remaining + 1):
                    if remaining % j == 0:
                        if is_prime(j):
                            k = remaining // j
                            if is_prime(k):
                                return True
    return False

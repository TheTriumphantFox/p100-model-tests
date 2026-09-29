def is_multiply_prime(a):
    """Write a function that returns true if the given number is the multiplication of 3 prime numbers
    and false otherwise.
    Knowing that (a) is less then 100.
    Example:
    is_multiply_prime(30) == True
    30 = 2 * 3 * 5
    """

    def is_prime(n):
        if n <= 1:
            return False
        if n == 2:
            return True
        if n % 2 == 0:
            return False
        for i in range(3, int(n**0.5) + 1, 2):
            if n % i == 0:
                return False
        return True

    if a < 2:
        return False

    primes = []
    n = a
    for i in range(2, n + 1):
        while n % i == 0 and is_prime(i):
            primes.append(i)
            n = n // i
            if len(primes) > 3:
                return False

    return len(primes) == 3

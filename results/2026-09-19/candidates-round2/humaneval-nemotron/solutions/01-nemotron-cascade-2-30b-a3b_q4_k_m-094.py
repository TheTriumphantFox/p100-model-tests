def skjkasdkd(lst):
    """Return the sum of the digits of the largest prime in the list.
    If there is no prime number, return 0.
    """
    def is_prime(n):
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

    max_prime = None
    for num in lst:
        if is_prime(num):
            if max_prime is None or num > max_prime:
                max_prime = num

    if max_prime is None:
        return 0

    return sum(int(d) for d in str(max_prime))

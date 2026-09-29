def skjkasdkd(lst):
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

    def digit_sum(n):
        s = 0
        while n > 0:
            s += n % 10
            n //= 10
        return s

    max_prime = None
    for num in lst:
        if is_prime(num):
            if max_prime is None or num > max_prime:
                max_prime = num

    return digit_sum(max_prime)

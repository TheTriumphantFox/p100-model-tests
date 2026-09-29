def prime_length(string):
    """Return True if the length of `string` is a prime number, otherwise False."""
    n = len(string)
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

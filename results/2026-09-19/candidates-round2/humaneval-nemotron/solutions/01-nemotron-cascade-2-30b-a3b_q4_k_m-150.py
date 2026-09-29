def x_or_y(n, x, y):
    """Return x if n is prime, otherwise return y."""
    if n < 2:
        return y
    if n == 2:
        return x
    if n % 2 == 0:
        return y
    i = 3
    while i * i <= n:
        if n % i == 0:
            return y
        i += 2
    return x

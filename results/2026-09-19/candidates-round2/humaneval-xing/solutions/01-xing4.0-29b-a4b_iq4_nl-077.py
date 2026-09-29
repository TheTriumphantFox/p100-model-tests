def iscube(a):
    if a == 0:
        return True
    sign = 1 if a > 0 else -1
    n = int(abs(a) ** (1/3)) + 1
    while n * n * n <= abs(a):
        n += 1
    return sign * n * n * n == a

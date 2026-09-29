def rounded_avg(n, m):
    if n > m:
        return -1
    total = sum(range(n, m + 1))
    count = m - n + 1
    avg = total / count
    rounded = round(avg)
    return bin(rounded)

def count_nums(arr):
    count = 0
    for num in arr:
        if num < 0:
            num = -num
        s = str(num)
        total = sum(int(d) for d in s)
        if total > 0:
            count += 1
    return count

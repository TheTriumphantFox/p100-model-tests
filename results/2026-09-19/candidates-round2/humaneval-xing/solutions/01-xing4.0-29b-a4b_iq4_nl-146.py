def specialFilter(nums):
    count = 0
    for num in nums:
        if num <= 10:
            continue
        abs_num = abs(num)
        first_digit = abs_num // (10 ** (len(str(abs_num)) - 1))
        last_digit = abs_num % 10
        if first_digit % 2 == 1 and last_digit % 2 == 1:
            count += 1
    return count

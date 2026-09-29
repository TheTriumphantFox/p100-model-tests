def count_nums(arr):
    """
    Write a function count_nums which takes an array of integers and returns
    the number of elements which has a sum of digits > 0.
    If a number is negative, then its first signed digit will be negative:
    e.g. -123 has signed digits -1, 2, and 3.
    >>> count_nums([]) == 0
    >>> count_nums([-1, 11, -11]) == 1
    >>> count_nums([1, 1, 2]) == 3
    """
    count = 0
    for num in arr:
        if num == 0:
            continue
        if num > 0:
            digit_sum = sum(int(d) for d in str(num))
        else:
            # For negative numbers, the first digit is negative
            s = str(num)
            # s starts with '-'
            first_digit = -int(s[1])
            rest_digits = sum(int(d) for d in s[2:])
            digit_sum = first_digit + rest_digits
        if digit_sum > 0:
            count += 1
    return count

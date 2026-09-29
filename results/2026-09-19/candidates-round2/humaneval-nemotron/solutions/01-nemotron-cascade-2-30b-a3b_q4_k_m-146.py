def specialFilter(nums):
    """Return the count of numbers in the list that are greater than 10 and have
    both first and last digits odd (1, 3, 5, 7, 9).

    Example:
        specialFilter([15, -73, 14, -15]) => 1
        specialFilter([33, -2, -3, 45, 21, 109]) => 2
    """
    def first_last_odd(n):
        # Work with absolute value to ignore sign
        n = abs(n)
        # Convert to string to easily access first and last digits
        s = str(n)
        first_digit = int(s[0])
        last_digit = int(s[-1])
        # Check if both digits are odd
        return (first_digit % 2 == 1) and (last_digit % 2 == 1)

    count = 0
    for num in nums:
        if num > 10 and first_last_odd(num):
            count += 1
    return count

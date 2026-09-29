def specialFilter(nums):
    """Write a function that takes an array of numbers as input and returns 
    the number of elements in the array that are greater than 10 and both 
    first and last digits of a number are odd (1, 3, 5, 7, 9).
    For example:
    specialFilter([15, -73, 14, -15]) => 1 
    specialFilter([33, -2, -3, 45, 21, 109]) => 2
    """
    count = 0
    for num in nums:
        if num <= 10:
            continue
        # Get the absolute value to handle negative numbers, but the problem says greater than 10, so num is positive
        # Actually, the examples include negative numbers but they are filtered out by num > 10
        # Let's work with the absolute value for digit extraction
        abs_num = abs(num)
        # Get the last digit
        last_digit = abs_num % 10
        # Get the first digit
        first_digit = abs_num
        while first_digit >= 10:
            first_digit //= 10
        
        if last_digit in (1, 3, 5, 7, 9) and first_digit in (1, 3, 5, 7, 9):
            count += 1
    return count

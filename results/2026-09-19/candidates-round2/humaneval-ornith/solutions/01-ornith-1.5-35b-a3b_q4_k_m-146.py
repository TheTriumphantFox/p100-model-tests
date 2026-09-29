def specialFilter(nums):
    """Write a function that takes an array of numbers as input and returns 
    the number of elements in the array that are greater than 10 and both 
    first and last digits of a number are odd (1, 3, 5, 7, 9).
    For example:
    specialFilter([15, -73, 14, -15]) => 1 
    specialFilter([33, -2, -3, 45, 21, 109]) => 2
    """
    def is_odd_digit(d):
        return d in {1, 3, 5, 7, 9}

    count = 0
    for num in nums:
        if num > 10:
            s = str(abs(num))
            first = int(s[0])
            last = int(s[-1])
            if is_odd_digit(first) and is_odd_digit(last):
                count += 1
    return count

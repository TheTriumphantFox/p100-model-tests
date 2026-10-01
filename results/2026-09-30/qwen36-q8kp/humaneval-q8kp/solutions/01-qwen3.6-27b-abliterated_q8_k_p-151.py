def double_the_difference(lst):
    '''
    Given a list of numbers, return the sum of squares of the numbers
    in the list that are odd. Ignore numbers that are negative or not integers.
    
    double_the_difference([1, 3, 2, 0]) == 1 + 9 + 0 + 0 = 10
    double_the_difference([-1, -2, 0]) == 0
    double_the_difference([9, -2]) == 81
    double_the_difference([0]) == 0  
   
    If the input list is empty, return 0.
    '''
    total = 0
    for num in lst:
        # Check if the number is an integer (not float, etc.)
        # We need to handle cases where num might be a float that represents an integer
        # But the problem says "not integers", so we check isinstance
        if isinstance(num, bool):
            # bool is a subclass of int in Python, so we need to exclude it
            continue
        if isinstance(num, int):
            if num >= 0 and num % 2 == 1:
                total += num * num
    return total

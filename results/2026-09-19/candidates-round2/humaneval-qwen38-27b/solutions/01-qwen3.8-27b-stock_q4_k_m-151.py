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
        # Check if it's an integer (not float, not bool)
        if isinstance(num, bool):
            continue
        if not isinstance(num, int):
            continue
        # Ignore negative numbers
        if num < 0:
            continue
        # Check if odd
        if num % 2 != 0:
            total += num * num
    return total

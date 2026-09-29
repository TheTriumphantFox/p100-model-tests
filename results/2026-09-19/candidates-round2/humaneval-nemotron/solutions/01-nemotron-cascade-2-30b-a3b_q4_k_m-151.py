def double_the_difference(lst):
    """
    Given a list of numbers, return the sum of squares of the numbers
    in the list that are odd. Ignore numbers that are negative or not integers.

    double_the_difference([1, 3, 2, 0]) == 1 + 9 + 0 + 0 = 10
    double_the_difference([-1, -2, 0]) == 0
    double_the_difference([9, -2]) == 81
    double_the_difference([0]) == 0  

    If the input list is empty, return 0.
    """
    total = 0
    for x in lst:
        # Check if x is an integer (bool is a subclass of int, but we treat True/False as non‑integers)
        if isinstance(x, int) and not isinstance(x, bool):
            if x >= 0 and x % 2 == 1:   # non‑negative odd integer
                total += x * x
    return total

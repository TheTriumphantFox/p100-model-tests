def starts_one_ends(n):
    """
    Given a positive integer n, return the count of the numbers of n-digit
    positive integers that start or end with 1.
    """
    if n == 1:
        return 1
    
    # Total n-digit numbers: from 10^(n-1) to 10^n - 1
    # Count numbers that start with 1: 10^(n-1)
    # Count numbers that end with 1: 10^(n-1)
    # Count numbers that both start and end with 1: 10^(n-2) (for n >= 2)
    
    start_with_1 = 10 ** (n - 1)
    end_with_1 = 10 ** (n - 1)
    both = 10 ** (n - 2) if n >= 2 else 0
    
    return start_with_1 + end_with_1 - both

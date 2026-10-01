def starts_one_ends(n):
    """
    Given a positive integer n, return the count of the numbers of n-digit
    positive integers that start or end with 1.
    """
    if n == 1:
        # For 1-digit numbers, the only number that starts or ends with 1 is 1 itself.
        return 1
    
    # n-digit numbers range from 10^(n-1) to 10^n - 1
    # Count numbers that start with 1:
    #   First digit is 1, remaining n-1 digits can be anything (0-9)
    #   So there are 10^(n-1) such numbers.
    # Count numbers that end with 1:
    #   Last digit is 1, first digit can be 1-9 (9 choices), remaining n-2 digits can be anything (10^(n-2) choices)
    #   So there are 9 * 10^(n-2) such numbers.
    # But we've double-counted numbers that both start AND end with 1.
    #   First digit is 1, last digit is 1, remaining n-2 digits can be anything.
    #   So there are 10^(n-2) such numbers.
    # By inclusion-exclusion:
    #   Total = starts_with_1 + ends_with_1 - both_start_and_end_with_1
    #         = 10^(n-1) + 9*10^(n-2) - 10^(n-2)
    #         = 10^(n-1) + 8*10^(n-2)
    
    starts_with_1 = 10 ** (n - 1)
    ends_with_1 = 9 * (10 ** (n - 2))
    both = 10 ** (n - 2)
    
    return starts_with_1 + ends_with_1 - both

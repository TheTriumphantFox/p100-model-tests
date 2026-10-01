def starts_one_ends(n):
    """
    Given a positive integer n, return the count of the numbers of n-digit
    positive integers that start or end with 1.
    """
    if n <= 0:
        return 0
    if n == 1:
        # 1-digit numbers: 1-9. Those starting or ending with 1: just 1.
        return 1
    
    # n-digit numbers range from 10^(n-1) to 10^n - 1
    # Count numbers that start with 1 OR end with 1
    # Use inclusion-exclusion: |A ∪ B| = |A| + |B| - |A ∩ B|
    
    # A: numbers that start with 1
    # First digit is 1, remaining n-1 digits can be anything (0-9)
    # So there are 10^(n-1) such numbers
    starts_with_1 = 10 ** (n - 1)
    
    # B: numbers that end with 1
    # Last digit is 1, first digit can be 1-9 (9 choices), middle n-2 digits can be 0-9 (10 choices each)
    # So there are 9 * 10^(n-2) such numbers
    ends_with_1 = 9 * (10 ** (n - 2))
    
    # A ∩ B: numbers that start with 1 AND end with 1
    # First digit is 1, last digit is 1, middle n-2 digits can be 0-9 (10 choices each)
    # So there are 10^(n-2) such numbers
    starts_and_ends_with_1 = 10 ** (n - 2)
    
    return starts_with_1 + ends_with_1 - starts_and_ends_with_1

def starts_one_ends(n):
    """
    Given a positive integer n, return the count of the numbers of n-digit
    positive integers that start or end with 1.
    """
    if n <= 0:
        return 0
    
    # Count of n-digit positive integers: 9 * 10^(n-1)
    # We need to count how many of these start with 1 OR end with 1.
    
    # Let's think about this differently.
    # For n-digit numbers, the range is from 10^(n-1) to 10^n - 1.
    # Total n-digit numbers: 9 * 10^(n-1)
    
    # Numbers that start with 1: These are numbers from 10^(n-1) to 2*10^(n-1) - 1.
    # Count = 10^(n-1)
    
    # Numbers that end with 1: These are numbers where the last digit is 1.
    # In any range of consecutive integers, roughly 1/10 end with 1.
    # For n-digit numbers, the count of numbers ending with 1 is 9 * 10^(n-2) for n >= 2.
    # For n = 1: numbers 1-9, only 1 ends with 1, so count = 1.
    
    # We need to use inclusion-exclusion: |A ∪ B| = |A| + |B| - |A ∩ B|
    # A = numbers starting with 1, B = numbers ending with 1
    # A ∩ B = numbers starting AND ending with 1
    
    # For n = 1: numbers 1-9. Start with 1: {1}. End with 1: {1}. Intersection: {1}.
    # Count = 1 + 1 - 1 = 1
    
    # For n >= 2:
    # |A| = 10^(n-1) (numbers from 10^(n-1) to 2*10^(n-1)-1)
    # |B| = 9 * 10^(n-2) (numbers ending with 1 among n-digit numbers)
    # |A ∩ B|: numbers that start with 1 AND end with 1.
    # These are numbers of the form 1...1 with n digits.
    # The first digit is 1, the last digit is 1, middle n-2 digits can be anything.
    # Count = 10^(n-2) for n >= 2. For n = 1, count = 1.
    
    if n == 1:
        return 1
    
    count_start = 10 ** (n - 1)
    count_end = 9 * 10 ** (n - 2)
    count_both = 10 ** (n - 2)
    
    return count_start + count_end - count_both

def starts_one_ends(n):
    """
    Given a positive integer n, return the count of the numbers of n-digit
    positive integers that start or end with 1.
    """
    if n == 1:
        return 1
    # Numbers starting with 1: 1 * 10^(n-1) to 1 * 10^(n-1) + 10^(n-1) - 1
    # Numbers ending with 1: 10^(n-1) to 10^n - 1, step 10
    # Using inclusion-exclusion principle to avoid double-counting numbers that start and end with 1
    start_with_1 = 10 ** (n - 1)
    end_with_1 = 10 ** (n - 1)
    start_and_end_with_1 = 10 ** (n - 1) + 1 if n > 1 else 1
    return start_with_1 + end_with_1 - start_and_end_with_1

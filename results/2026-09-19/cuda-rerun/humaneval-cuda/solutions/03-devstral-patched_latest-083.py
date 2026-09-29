def starts_one_ends(n):
    """
    Given a positive integer n, return the count of the numbers of n-digit
    positive integers that start or end with 1.
    """
    if n == 1:
        return 1
    # Numbers starting with 1: 1 * 10^(n-1) to 1 * 10^(n-1) + 10^(n-1) - 1
    # Numbers ending with 1: 10^(n-1) to 10^n - 1, step 10
    # Numbers starting and ending with 1: 1 * 10^(n-1) + 1
    # Using inclusion-exclusion principle
    return 10 ** (n - 1) + 10 ** (n - 1) - 1

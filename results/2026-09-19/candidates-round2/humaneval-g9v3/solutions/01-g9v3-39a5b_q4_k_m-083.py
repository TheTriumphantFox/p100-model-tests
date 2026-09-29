def starts_one_ends(n):
    """
    Given a positive integer n, return the count of the numbers of n-digit
    positive integers that start or end with 1.
    """
    if n == 1:
        return 1
    # Total n-digit numbers: 9 * 10^(n-1)
    # Numbers starting with 1: 1 * 10^(n-1)
    # Numbers ending with 1: 9 * 10^(n-2) (first digit can't be 0)
    # Numbers both starting and ending with 1: 1 * 10^(n-2)
    # By inclusion-exclusion: start_with_1 + end_with_1 - both
    start_with_1 = 10 ** (n - 1)
    end_with_1 = 9 * (10 ** (n - 2))
    both = 10 ** (n - 2)
    return start_with_1 + end_with_1 - both

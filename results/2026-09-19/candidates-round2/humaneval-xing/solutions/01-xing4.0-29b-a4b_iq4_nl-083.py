def starts_one_ends(n):
    """
    Given a positive integer n, return the count of the numbers of n-digit
    positive integers that start or end with 1.
    """
    if n == 1:
        return 1
    # Numbers starting with 1: first digit is 1, remaining n-1 digits can be anything (0-9)
    start_with_1 = 10 ** (n - 1)
    # Numbers ending with 1: last digit is 1, first digit cannot be 0, remaining n-2 digits can be anything (0-9)
    end_with_1 = 9 * (10 ** (n - 2))
    # Numbers starting AND ending with 1: first digit is 1, last digit is 1, middle n-2 digits can be anything
    both = 10 ** (n - 2) if n >= 2 else 1
    return start_with_1 + end_with_1 - both

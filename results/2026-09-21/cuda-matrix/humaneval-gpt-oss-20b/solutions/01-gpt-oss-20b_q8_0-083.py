def starts_one_ends(n: int) -> int:
    """
    Given a positive integer n, return the count of the numbers of n-digit
    positive integers that start or end with 1.
    """
    if n <= 0:
        raise ValueError("n must be a positive integer")

    # Count of n-digit numbers that start with 1:
    # The remaining (n-1) digits can be any of 0-9.
    start_with_one = 10 ** (n - 1)

    # Count of n-digit numbers that end with 1:
    # The first digit can be 1-9 (9 choices), the middle (n-2) digits can be 0-9.
    if n == 1:
        end_with_one = 1  # only the number 1
    else:
        end_with_one = 9 * (10 ** (n - 2))

    # Numbers that both start and end with 1 are counted twice,
    # so subtract them once.  These are numbers of the form
    # 1 * ... * 1, where the middle (n-2) digits can be 0-9.
    if n == 1:
        both_start_and_end_one = 1
    else:
        both_start_and_end_one = 10 ** (n - 2)

    return start_with_one + end_with_one - both_start_and_end_one

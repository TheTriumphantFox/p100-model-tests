def starts_one_ends(n: int) -> int:
    """
    Given a positive integer n, return the count of the numbers of n-digit
    positive integers that start or end with 1.
    """
    if n <= 0:
        raise ValueError("n must be a positive integer")

    # For a single-digit number, only the number 1 satisfies the condition.
    if n == 1:
        return 1

    # Count of n-digit numbers that start with 1:
    #   1 followed by any (n-1) digits: 10^(n-1) possibilities.
    start_with_1 = 10 ** (n - 1)

    # Count of n-digit numbers that end with 1:
    #   First digit can be 1-9 (9 options), middle (n-2) digits any 0-9,
    #   last digit fixed as 1.
    end_with_1 = 9 * (10 ** (n - 2))

    # Numbers counted twice (start and end with 1):
    #   1 followed by (n-2) digits, then 1: 10^(n-2) possibilities.
    both = 10 ** (n - 2)

    # Inclusion–exclusion principle
    return start_with_1 + end_with_1 - both

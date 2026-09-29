def make_a_pile(n: int) -> list[int]:
    """
    Given a positive integer n, you have to make a pile of n levels of stones.
    The first level has n stones.
    The number of stones in the next level is:
        - the next odd number if n is odd.
        - the next even number if n is even.
    Return the number of stones in each level in a list, where element at index
    i represents the number of stones in the level (i+1).

    Examples:
    >>> make_a_pile(3)
    [3, 5, 7]
    >>> make_a_pile(4)
    [4, 6, 8, 10]
    """
    if n <= 0:
        raise ValueError("n must be a positive integer")
    result = [n]
    for _ in range(1, n):
        result.append(result[-1] + 2)
    return result

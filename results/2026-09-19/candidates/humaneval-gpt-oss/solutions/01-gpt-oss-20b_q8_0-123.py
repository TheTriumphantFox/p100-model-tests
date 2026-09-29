def get_odd_collatz(n: int) -> list[int]:
    """
    Return a sorted list of the odd numbers that appear in the Collatz sequence
    starting from the positive integer n.

    Parameters
    ----------
    n : int
        A positive integer (n >= 1).

    Returns
    -------
    list[int]
        Sorted list of odd numbers in the Collatz sequence for n.

    Examples
    --------
    >>> get_odd_collatz(5)
    [1, 5]
    >>> get_odd_collatz(1)
    [1]
    >>> get_odd_collatz(3)
    [1, 3]
    """
    if n < 1:
        raise ValueError("n must be a positive integer")

    odd_numbers = set()
    current = n
    while True:
        if current % 2 == 1:
            odd_numbers.add(current)
        if current == 1:
            break
        if current % 2 == 0:
            current //= 2
        else:
            current = 3 * current + 1

    return sorted(odd_numbers)

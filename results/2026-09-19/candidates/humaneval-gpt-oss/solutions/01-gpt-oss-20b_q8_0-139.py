def special_factorial(n: int) -> int:
    """
    Compute the Brazilian factorial of n:
    brazilian_factorial(n) = n! * (n-1)! * ... * 1!
    where n > 0.

    Parameters
    ----------
    n : int
        Positive integer whose Brazilian factorial is to be computed.

    Returns
    -------
    int
        The Brazilian factorial of n.

    Examples
    --------
    >>> special_factorial(4)
    288
    """
    if n <= 0:
        raise ValueError("n must be a positive integer")

    result = 1
    current_factorial = 1
    for i in range(1, n + 1):
        current_factorial *= i          # i!
        result *= current_factorial     # multiply by i!
    return result

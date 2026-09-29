def simplify(x: str, n: str) -> bool:
    """
    Return True if the product of the two fractions x and n is an integer,
    otherwise return False.

    Parameters
    ----------
    x : str
        A fraction in the form "numerator/denominator".
    n : str
        A fraction in the form "numerator/denominator".

    Returns
    -------
    bool
        True if the product is an integer, False otherwise.
    """
    # Parse the fractions
    a, b = map(int, x.split('/'))
    c, d = map(int, n.split('/'))

    # Compute the product numerator and denominator
    num = a * c
    den = b * d

    # The product is an integer if the denominator divides the numerator
    return num % den == 0

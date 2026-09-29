from fractions import Fraction

def simplify(x: str, n: str) -> bool:
    """
    Determines whether the product of two fractions represented as strings evaluates to a whole number.

    Each input string has the format "<numerator>/<denominator>" where both numerator and denominator
    are positive integers. The function returns True if the product of the two fractions is an integer,
    otherwise it returns False.

    Examples:
        simplify("1/5", "5/1")   -> True  (1/5 * 5/1 = 1)
        simplify("1/6", "2/1")   -> False (1/6 * 2/1 = 1/3)
        simplify("7/10", "10/2") -> False (7/10 * 10/2 = 7/2)
    """
    # Parse the two fraction strings into Fraction objects.
    frac_x = Fraction(*map(int, x.split('/')))
    frac_n = Fraction(*map(int, n.split('/')))

    # Multiply the fractions.
    product = frac_x * frac_n

    # The product is a whole number if its denominator is 1.
    return product.denominator == 1

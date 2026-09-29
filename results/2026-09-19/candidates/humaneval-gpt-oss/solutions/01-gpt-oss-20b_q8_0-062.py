def derivative(xs: list):
    """ xs represent coefficients of a polynomial.
    xs[0] + xs[1] * x + xs[2] * x^2 + ....
     Return derivative of this polynomial in the same form.
    >>> derivative([3, 1, 2, 4, 5])
    [1, 4, 12, 20]
    >>> derivative([1, 2, 3])
    [2, 6]
    """
    # If the polynomial has no terms or only a constant term, its derivative is zero.
    if len(xs) <= 1:
        return []

    # Compute derivative: coefficient of x^n becomes n * coefficient of x^n
    return [i * xs[i] for i in range(1, len(xs))]

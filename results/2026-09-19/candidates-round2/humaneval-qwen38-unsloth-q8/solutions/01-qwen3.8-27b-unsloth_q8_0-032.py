import math


def poly(xs: list, x: float):
    """
    Evaluates polynomial with coefficients xs at point x.
    return xs[0] + xs[1] * x + xs[1] * x^2 + .... xs[n] * x^n
    """
    return sum([coeff * math.pow(x, i) for i, coeff in enumerate(xs)])


def find_zero(xs: list):
    """ xs are coefficients of a polynomial.
    find_zero find x such that poly(x) = 0.
    find_zero returns only only zero point, even if there are many.
    Moreover, find_zero only takes list xs having even number of coefficients
    and largest non zero coefficient as it guarantees
    a solution.
    >>> round(find_zero([1, 2]), 2) # f(x) = 1 + 2x
    -0.5
    >>> round(find_zero([-6, 11, -6, 1]), 2) # (x - 1) * (x - 2) * (x - 3) = -6 + 11x - 6x^2 + x^3
    1.0
    """
    # Use bisection method to find a zero
    # We need to find an interval [a, b] where poly(a) and poly(b) have opposite signs
    
    # First, let's find a reasonable range
    # The problem states that xs has even number of coefficients and largest non-zero coefficient
    # guarantees a solution. Let's try to find a zero using bisection.
    
    # Try a range from -100 to 100
    a = -100.0
    b = 100.0
    
    # Check if we have a sign change
    fa = poly(xs, a)
    fb = poly(xs, b)
    
    # If no sign change in this range, try expanding
    if fa * fb > 0:
        # Try larger range
        for scale in [1000, 10000, 100000]:
            a = -scale
            b = scale
            fa = poly(xs, a)
            fb = poly(xs, b)
            if fa * fb <= 0:
                break
    
    # If still no sign change, try to find one by scanning
    if fa * fb > 0:
        # Scan for a sign change
        found = False
        step = 1.0
        for i in range(-1000, 1001):
            x1 = i * step
            x2 = (i + 1) * step
            f1 = poly(xs, x1)
            f2 = poly(xs, x2)
            if f1 * f2 <= 0:
                a = x1
                b = x2
                fa = f1
                fb = f2
                found = True
                break
        if not found:
            # Return 0 as a fallback
            return 0.0
    
    # Bisection method
    for _ in range(100):
        mid = (a + b) / 2
        fm = poly(xs, mid)
        if abs(fm) < 1e-10:
            return mid
        if fa * fm <= 0:
            b = mid
            fb = fm
        else:
            a = mid
            fa = fm
    
    return (a + b) / 2

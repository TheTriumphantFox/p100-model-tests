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
    # Use bisection method to find a root
    # We need to find an interval [a, b] where poly(a) and poly(b) have opposite signs
    
    # Find bounds for bisection
    # Start with a reasonable range and expand if needed
    lo, hi = -100.0, 100.0
    
    # Find a valid interval where the function changes sign
    # We'll search for a sign change
    def f(x):
        return poly(xs, x)
    
    # Find bounds where we have a sign change
    # Try to find a and b such that f(a) * f(b) <= 0
    a, b = lo, hi
    fa, fb = f(a), f(b)
    
    # Expand the interval if needed to find a sign change
    max_iterations = 100
    iterations = 0
    while fa * fb > 0 and iterations < max_iterations:
        # Expand the interval
        lo *= 2
        hi *= 2
        a, b = lo, hi
        fa, fb = f(a), f(b)
        iterations += 1
    
    # If still no sign change, try a different approach
    if fa * fb > 0:
        # Try to find a sign change by scanning
        found = False
        prev_x = -100.0
        prev_f = f(prev_x)
        for i in range(1, 200):
            curr_x = -100.0 + i * 1.0
            curr_f = f(curr_x)
            if prev_f * curr_f <= 0:
                a, b = prev_x, curr_x
                fa, fb = prev_f, curr_f
                found = True
                break
            prev_x, prev_f = curr_x, curr_f
        if not found:
            # Return a reasonable default if no root found
            return 0.0
    
    # Bisection method
    for _ in range(100):
        mid = (a + b) / 2.0
        fm = f(mid)
        if abs(fm) < 1e-10:
            return mid
        if fa * fm <= 0:
            b = mid
            fb = fm
        else:
            a = mid
            fa = fm
    
    return (a + b) / 2.0

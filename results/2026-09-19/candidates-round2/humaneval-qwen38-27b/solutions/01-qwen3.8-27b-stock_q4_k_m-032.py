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
    # First, find a range where the function changes sign
    # We'll search in a reasonable range
    
    # Find a good initial range
    # For polynomials with even number of coefficients (odd degree), there's always at least one real root
    # Let's try to find a range [a, b] where poly(a) and poly(b) have opposite signs
    
    # Start with a small range and expand if needed
    a = -1.0
    b = 1.0
    
    # Expand the range until we find a sign change
    max_expansion = 100
    for _ in range(max_expansion):
        fa = poly(xs, a)
        fb = poly(xs, b)
        if fa * fb <= 0:
            break
        a *= 2
        b *= 2
    
    # If no sign change found, try a different approach
    if fa * fb > 0:
        # Try searching in a wider range
        a = -1000.0
        b = 1000.0
        fa = poly(xs, a)
        fb = poly(xs, b)
        if fa * fb > 0:
            # As a fallback, try to find a root using a simple search
            # This is a heuristic approach
            step = 0.1
            x = -1000.0
            prev_val = poly(xs, x)
            while x < 1000.0:
                x += step
                curr_val = poly(xs, x)
                if prev_val * curr_val <= 0:
                    a = x - step
                    b = x
                    break
                prev_val = curr_val
            else:
                # If we still haven't found a sign change, return 0 as a default
                return 0.0
    
    # Now use bisection to find the root
    for _ in range(100):  # 100 iterations should be enough for good precision
        mid = (a + b) / 2
        fmid = poly(xs, mid)
        if abs(fmid) < 1e-10:
            return mid
        if poly(xs, a) * fmid <= 0:
            b = mid
        else:
            a = mid
    
    return (a + b) / 2

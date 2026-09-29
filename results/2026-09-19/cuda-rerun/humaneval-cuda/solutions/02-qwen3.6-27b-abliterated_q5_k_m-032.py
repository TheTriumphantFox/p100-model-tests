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
    # Use binary search to find a root
    # We need to find a range [a, b] where poly(a) and poly(b) have opposite signs
    # Since the polynomial has even number of coefficients and the largest non-zero coefficient
    # guarantees a solution, we can search in a reasonable range.
    
    # First, let's find a good search range
    # For polynomials, roots are typically bounded. We'll use a large range and narrow down.
    
    # Use the bisection method
    # Find an interval [a, b] where poly(a) * poly(b) < 0
    
    # Start with a wide range
    a, b = -1000.0, 1000.0
    
    # Evaluate at endpoints
    fa = poly(xs, a)
    fb = poly(xs, b)
    
    # If they have opposite signs, we can bisect
    # If not, try to find a better interval
    if fa * fb > 0:
        # Try to find a root by scanning
        # Check many points to find a sign change
        step = 0.1
        for i in range(int((b - a) / step)):
            x1 = a + i * step
            x2 = a + (i + 1) * step
            f1 = poly(xs, x1)
            f2 = poly(xs, x2)
            if f1 * f2 <= 0:
                a, b = x1, x2
                fa, fb = f1, f2
                break
        else:
            # If no sign change found, try a different approach
            # Use Newton's method with a starting guess
            x = 0.0
            for _ in range(1000):
                fx = poly(xs, x)
                # Compute derivative
                deriv = sum([i * coeff * math.pow(x, i - 1) for i, coeff in enumerate(xs) if i > 0])
                if abs(deriv) < 1e-10:
                    x += 0.01
                    continue
                x_new = x - fx / deriv
                if abs(x_new - x) < 1e-10:
                    break
                x = x_new
            return x
    
    # Bisection method
    for _ in range(100):
        mid = (a + b) / 2.0
        fmid = poly(xs, mid)
        if abs(fmid) < 1e-10:
            return mid
        if fa * fmid < 0:
            b = mid
            fb = fmid
        else:
            a = mid
            fa = fmid
    
    return (a + b) / 2.0

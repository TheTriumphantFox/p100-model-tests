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
    
    # First, let's find a reasonable range to search
    # For polynomials, we can use Cauchy's bound or similar
    # Cauchy's bound: all real roots lie in [-M, M] where M = 1 + max(|coeff|/|leading_coeff|)
    
    # Find the degree and leading coefficient
    n = len(xs) - 1
    if n == 0:
        return 0.0
    
    # Find the highest degree with non-zero coefficient
    while n > 0 and xs[n] == 0:
        n -= 1
    
    leading_coeff = xs[n]
    if leading_coeff == 0:
        return 0.0
    
    # Cauchy's bound
    max_abs_coeff = max(abs(c) for c in xs[:n])
    M = 1 + max_abs_coeff / abs(leading_coeff)
    
    # Search in [-M, M] using bisection
    a = -M
    b = M
    
    fa = poly(xs, a)
    fb = poly(xs, b)
    
    # If signs are the same, we need to find a subinterval where they differ
    # Let's sample many points and find a sign change
    num_samples = 10000
    step = (b - a) / num_samples
    
    for i in range(num_samples):
        x1 = a + i * step
        x2 = a + (i + 1) * step
        f1 = poly(xs, x1)
        f2 = poly(xs, x2)
        if f1 * f2 <= 0:
            # Found a sign change, use bisection
            a, b = x1, x2
            fa, fb = f1, f2
            for _ in range(100):  # enough iterations for precision
                mid = (a + b) / 2
                fmid = poly(xs, mid)
                if abs(fmid) < 1e-12:
                    return mid
                if fa * fmid < 0:
                    b = mid
                    fb = fmid
                else:
                    a = mid
                    fa = fmid
            return (a + b) / 2
    
    # If no sign change found, return midpoint or try Newton's method
    # Fallback: use Newton's method from a starting point
    x = 0.0
    for _ in range(1000):
        fx = poly(xs, x)
        if abs(fx) < 1e-12:
            return x
        # Compute derivative
        deriv = sum([i * xs[i] * math.pow(x, i - 1) for i in range(1, len(xs))])
        if abs(deriv) < 1e-12:
            x += 0.1
            continue
        x = x - fx / deriv
    
    return x

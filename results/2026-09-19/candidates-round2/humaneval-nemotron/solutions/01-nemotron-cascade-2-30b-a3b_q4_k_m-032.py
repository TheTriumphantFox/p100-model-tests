import math
from typing import List, Optional

def poly(xs: List[float], x: float) -> float:
    """
    Evaluates polynomial with coefficients xs at point x.
    return xs[0] + xs[1] * x + xs[1] * x^2 + .... xs[n] * x^n
    """
    return sum(coeff * math.pow(x, i) for i, coeff in enumerate(xs))


def find_zero(xs: List[float]) -> Optional[float]:
    """
    xs are coefficients of a polynomial.
    find_zero finds x such that poly(x) = 0.
    find_zero returns only one zero point, even if there are many.
    Moreover, find_zero only takes list xs having even number of coefficients
    and largest non zero coefficient as it guarantees a solution.
    """
    if len(xs) % 2 != 0:
        raise ValueError("Number of coefficients must be even.")
    if all(c == 0 for c in xs):
        raise ValueError("All coefficients are zero.")
    if xs[-1] == 0:
        raise ValueError("Largest non-zero coefficient must be at the end.")
    
    a = xs[-1]
    b = xs[-2]
    c = a * b / 2.0
    d = c / b
    e = d / b
    f = e / b
    g = f / b
    h = g / b
    i = h / b
    j = i / b
    k = j / b
    l = k / b
    m = l / b
    n = m / b
    o = n / b
    p = o / b
    q = p / b
    r = q / b
    s = r / b
    t = s / b
    u = t / b
    v = u / b
    w = v / b
    x0 = w / b
    x0 = x0 - (poly(xs, x0) / poly(xs, x0 + 1e-6))
    return x0

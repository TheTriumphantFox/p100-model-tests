import math

def truncate_number(number: float) -> float:
    """Given a positive floating point number, return its decimal part.

    The decimal part is the fractional part of the number, i.e. the
    difference between the number and the largest integer not greater
    than the number.

    >>> truncate_number(3.5)
    0.5
    >>> truncate_number(10.0)
    0.0
    >>> truncate_number(0.123)
    0.123
    """
    if number < 0:
        raise ValueError("Number must be positive")
    return number - math.floor(number)

from typing import List


def rescale_to_unit(numbers: List[float]) -> List[float]:
    """Given a list of numbers (at least two elements), apply a linear transform
    so that the smallest number becomes 0 and the largest becomes 1.

    If all numbers are equal, the function returns a list of zeros.

    >>> rescale_to_unit([1.0, 2.0, 3.0, 4.0, 5.0])
    [0.0, 0.25, 0.5, 0.75, 1.0]
    """
    if not numbers:
        raise ValueError("Input list must contain at least one element")

    min_val = min(numbers)
    max_val = max(numbers)

    # Avoid division by zero when all values are equal
    if min_val == max_val:
        return [0.0 for _ in numbers]

    scale = max_val - min_val
    return [(x - min_val) / scale for x in numbers]

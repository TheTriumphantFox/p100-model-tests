from typing import List, Tuple
import itertools

def find_closest_elements(numbers: List[float]) -> Tuple[float, float]:
    """
    From a supplied list of numbers (of length at least two) select and return two that are the closest to each
    other and return them in order (smaller number, larger number).

    >>> find_closest_elements([1.0, 2.0, 3.0, 4.0, 5.0, 2.2])
    (2.0, 2.2)
    >>> find_closest_elements([1.0, 2.0, 3.0, 4.0, 5.0, 2.0])
    (2.0, 2.0)
    """
    if len(numbers) < 2:
        raise ValueError("At least two numbers are required")

    # Initialize with the first pair
    min_diff = float("inf")
    best_pair = (numbers[0], numbers[1])

    for a, b in itertools.combinations(numbers, 2):
        diff = abs(a - b)
        if diff < min_diff:
            min_diff = diff
            best_pair = (a, b)

    # Return the pair in ascending order
    return tuple(sorted(best_pair))

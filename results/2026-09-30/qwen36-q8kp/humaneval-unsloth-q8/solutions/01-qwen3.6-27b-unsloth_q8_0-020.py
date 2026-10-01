from typing import List, Tuple


def find_closest_elements(numbers: List[float]) -> Tuple[float, float]:
    """ From a supplied list of numbers (of length at least two) select and return two that are the closest to each
    other and return them in order (smaller number, larger number).
    >>> find_closest_elements([1.0, 2.0, 3.0, 4.0, 5.0, 2.2])
    (2.0, 2.2)
    >>> find_closest_elements([1.0, 2.0, 3.0, 4.0, 5.0, 2.0])
    (2.0, 2.0)
    """
    if len(numbers) < 2:
        raise ValueError("List must contain at least two numbers")
    
    # Sort the numbers to make it easier to find closest pairs
    sorted_nums = sorted(numbers)
    
    min_diff = float('inf')
    closest_pair = (sorted_nums[0], sorted_nums[1])
    
    for i in range(len(sorted_nums) - 1):
        diff = sorted_nums[i + 1] - sorted_nums[i]
        if diff < min_diff:
            min_diff = diff
            closest_pair = (sorted_nums[i], sorted_nums[i + 1])
    
    return closest_pair

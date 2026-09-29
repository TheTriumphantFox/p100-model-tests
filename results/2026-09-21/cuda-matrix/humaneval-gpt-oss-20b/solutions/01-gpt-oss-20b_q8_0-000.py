from typing import List


def has_close_elements(numbers: List[float], threshold: float) -> bool:
    """Check if any two numbers in the list are closer than the given threshold.

    The function sorts the list first, then only adjacent pairs need to be checked,
    which is sufficient because the smallest difference in a sorted list
    must occur between consecutive elements.

    Args:
        numbers: List of numeric values.
        threshold: The maximum allowed distance between two numbers.

    Returns:
        True if any two numbers are closer than threshold, False otherwise.

    Examples:
        >>> has_close_elements([1.0, 2.0, 3.0], 0.5)
        False
        >>> has_close_elements([1.0, 2.8, 3.0, 4.0, 5.0, 2.0], 0.3)
        True
    """
    if len(numbers) < 2:
        return False

    sorted_nums = sorted(numbers)
    for i in range(1, len(sorted_nums)):
        if abs(sorted_nums[i] - sorted_nums[i - 1]) < threshold:
            return True
    return False

from typing import List


def remove_duplicates(numbers: List[int]) -> List[int]:
    """From a list of integers, remove all elements that occur more than once.
    Keep order of elements left the same as in the input.

    >>> remove_duplicates([1, 2, 3, 2, 4])
    [1, 3, 4]
    """
    # Count occurrences of each number
    counts = {}
    for n in numbers:
        counts[n] = counts.get(n, 0) + 1

    # Keep only numbers that appear exactly once
    return [n for n in numbers if counts[n] == 1]

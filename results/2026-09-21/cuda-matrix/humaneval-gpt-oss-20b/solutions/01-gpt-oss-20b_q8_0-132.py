def is_nested(string: str) -> bool:
    """
    Return True if the input string of '[' and ']' contains a subsequence
    that forms a valid bracket sequence with at least one nested pair.
    A nested subsequence can be represented by the pattern "[[...]]".
    """
    # Find positions of all '['
    left_positions = [i for i, ch in enumerate(string) if ch == "["]
    if len(left_positions) < 2:
        return False

    # Index of the second '['
    second_left = left_positions[1]

    # Count ']' after the second '['
    right_count = sum(1 for ch in string[second_left + 1 :] if ch == "]")

    return right_count >= 2

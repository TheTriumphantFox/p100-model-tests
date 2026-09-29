def count_distinct_characters(string: str) -> int:
    """Given a string, return the number of distinct characters it contains,
    ignoring case.

    >>> count_distinct_characters('xyzXYZ')
    3
    >>> count_distinct_characters('Jerry')
    4
    """
    # Convert all characters to a common case (lowercase) and use a set
    # to automatically deduplicate them.
    return len(set(string.lower()))

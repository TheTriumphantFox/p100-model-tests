def reverse_delete(s: str, c: str) -> tuple[str, bool]:
    """
    Delete all characters from `s` that appear in `c` and check if the
    resulting string is a palindrome.

    Parameters
    ----------
    s : str
        The original string.
    c : str
        String containing characters to delete from `s`.

    Returns
    -------
    tuple[str, bool]
        A tuple containing the cleaned string and a boolean indicating
        whether it is a palindrome.
    """
    # Build a set of characters to delete for O(1) lookups
    delete_set = set(c)

    # Filter out characters present in delete_set
    cleaned = "".join(ch for ch in s if ch not in delete_set)

    # Check if cleaned string is a palindrome
    is_palindrome = cleaned == cleaned[::-1]

    return cleaned, is_palindrome

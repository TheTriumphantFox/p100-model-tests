def vowels_count(s: str) -> int:
    """Return the number of vowels in the string `s`.

    Vowels are 'a', 'e', 'i', 'o', 'u' (case‑insensitive). The letter
    'y' (or 'Y') is considered a vowel only when it appears as the last
    character of the string.

    Parameters
    ----------
    s : str
        The input string.

    Returns
    -------
    int
        The count of vowels in `s`.

    Examples
    --------
    >>> vowels_count("abcde")
    2
    >>> vowels_count("ACEDY")
    3
    """
    if not s:
        return 0

    vowels = set("aeiouAEIOU")
    count = 0

    for i, ch in enumerate(s):
        if ch in vowels:
            count += 1
        elif ch in "yY" and i == len(s) - 1:
            count += 1

    return count

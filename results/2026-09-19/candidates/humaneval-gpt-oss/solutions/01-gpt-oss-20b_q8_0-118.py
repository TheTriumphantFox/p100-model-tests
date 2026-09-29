def get_closest_vowel(word: str) -> str:
    """
    Find the closest vowel that is surrounded by consonants, searching from the right side.
    Vowels at the beginning or end of the word are ignored.
    Returns the vowel if found, otherwise an empty string.
    """
    vowels = set("aeiouAEIOU")
    n = len(word)
    # iterate from right to left, skip last character
    for i in range(n - 1, 0, -1):
        ch = word[i]
        if ch in vowels:
            # ensure not at start or end
            if i == 0 or i == n - 1:
                continue
            left = word[i - 1]
            right = word[i + 1] if i + 1 < n else None
            if left not in vowels and right not in vowels:
                return ch
    return ""

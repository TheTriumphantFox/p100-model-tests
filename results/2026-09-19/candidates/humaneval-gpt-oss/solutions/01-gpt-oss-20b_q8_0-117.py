def select_words(s, n):
    """Return a list of words from `s` that contain exactly `n` consonants.
    
    Parameters
    ----------
    s : str
        Input string containing only letters and spaces.
    n : int
        Target number of consonants.
    
    Returns
    -------
    list[str]
        Words that have exactly `n` consonants, in the order they appear.
    """
    if not s:
        return []

    vowels = set("aeiouAEIOU")
    result = []

    for word in s.split():
        # Count consonants: letters that are not vowels
        consonant_count = sum(1 for ch in word if ch.isalpha() and ch not in vowels)
        if consonant_count == n:
            result.append(word)

    return result

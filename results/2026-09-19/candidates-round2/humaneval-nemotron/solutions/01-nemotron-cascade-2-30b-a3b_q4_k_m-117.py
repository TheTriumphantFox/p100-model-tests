def select_words(s, n):
    """Return a list of words from s that contain exactly n consonants.
    
    Words are separated by spaces. Consonants are letters that are not vowels
    (a, e, i, o, u). The function is case‑insensitive when counting consonants.
    If s is empty, an empty list is returned.
    """
    if not s:
        return []

    vowels = set('aeiou')
    result = []

    for word in s.split():
        # Count consonants in the word (ignore non‑letters, though input guarantees letters)
        consonant_count = sum(1 for ch in word.lower() if ch.isalpha() and ch not in vowels)
        if consonant_count == n:
            result.append(word)

    return result

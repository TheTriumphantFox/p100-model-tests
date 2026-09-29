def find_max(words):
    """
    Write a function that accepts a list of strings.
    The list contains different words. Return the word with maximum number
    of unique characters. If multiple strings have maximum number of unique
    characters, return the one which comes first in lexicographical order.

    >>> find_max(["name", "of", "string"])
    'string'
    >>> find_max(["name", "enam", "game"])
    'enam'
    >>> find_max(["aaaaaaa", "bb", "cc"])
    'aaaaaaa'
    """
    best_word = None
    best_unique = -1
    for w in words:
        uniq = len(set(w))
        if uniq > best_unique:
            best_unique = uniq
            best_word = w
        elif uniq == best_unique:
            if w < best_word:
                best_word = w
    return best_word

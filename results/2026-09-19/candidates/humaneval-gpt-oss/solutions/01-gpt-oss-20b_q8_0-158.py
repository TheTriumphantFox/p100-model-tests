def find_max(words):
    """
    Return the word with the maximum number of unique characters.
    If multiple words tie, return the lexicographically smallest one.
    """
    best_word = ""
    best_unique = -1
    for word in words:
        unique_count = len(set(word))
        if unique_count > best_unique:
            best_unique = unique_count
            best_word = word
        elif unique_count == best_unique:
            if word < best_word:
                best_word = word
    return best_word

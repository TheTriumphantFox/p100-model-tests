def find_max(words):
    """Write a function that accepts a list of strings.
    The list contains different words. Return the word with maximum number
    of unique characters. If multiple strings have maximum number of unique
    characters, return the one which comes first in lexicographical order.

    find_max(["name", "of", "string"]) == "string"
    find_max(["name", "enam", "game"]) == "enam"
    find_max(["aaaaaaa", "bb" ,"cc"]) == "aaaaaaa"
    """
    if not words:
        return ""
    
    def score(word):
        return (len(set(word)), word)
    
    # We want to maximize the number of unique characters,
    # and break ties by lexicographical order (smallest first)
    # So we sort by (-unique_count, word) and take the first
    best = max(words, key=lambda w: (len(set(w)), [-ord(c) for c in w]))
    
    # Actually, let's think more carefully:
    # We want the word with maximum unique characters.
    # If tie, return the one that comes first in lexicographical order.
    # So we can sort by: primary key = len(set(w)) descending, secondary key = w ascending
    
    # Using max with a key: we want to maximize unique count, and for ties, minimize lexicographically
    # One approach: sort all words by (-len(set(w)), w) and take the first
    sorted_words = sorted(words, key=lambda w: (-len(set(w)), w))
    return sorted_words[0]

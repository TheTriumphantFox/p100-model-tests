def histogram(test):
    """Given a string representing a space separated lowercase letters, return a dictionary
    of the letter with the most repetition and containing the corresponding count.
    If several letters have the same occurrence, return all of them.

    Example:
    histogram('a b c') == {'a': 1, 'b': 1, 'c': 1}
    histogram('a b b a') == {'a': 2, 'b': 2}
    histogram('a b c a b') == {'a': 2, 'b': 2}
    histogram('b b b b a') == {'b': 4}
    histogram('') == {}

    """
    if not test.strip():
        return {}

    letters = test.split()
    count = {}
    max_count = 0

    for letter in letters:
        count[letter] = count.get(letter, 0) + 1
        if count[letter] > max_count:
            max_count = count[letter]

    result = {letter: cnt for letter, cnt in count.items() if cnt == max_count}
    return result

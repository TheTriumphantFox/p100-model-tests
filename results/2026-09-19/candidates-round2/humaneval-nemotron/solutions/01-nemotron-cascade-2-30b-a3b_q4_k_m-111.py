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
    # Split the input string into individual letters; handle empty input
    letters = test.split() if test else []

    # Count occurrences of each letter
    counts = {}
    for ch in letters:
        counts[ch] = counts.get(ch, 0) + 1

    # If there are no letters, return an empty dictionary
    if not counts:
        return {}

    # Determine the maximum count
    max_count = max(counts.values())

    # Build the result dictionary with all letters that have the maximum count
    result = {ch: cnt for ch, cnt in counts.items() if cnt == max_count}
    return result

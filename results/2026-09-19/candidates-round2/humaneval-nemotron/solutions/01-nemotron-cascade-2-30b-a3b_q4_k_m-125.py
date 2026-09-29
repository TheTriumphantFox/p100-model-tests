def split_words(txt):
    """
    Given a string of words, return a list of words split on whitespace,
    if no whitespaces exists in the text you should split on commas ','
    if no commas exists you should return the number of lower-case letters
    with odd order in the alphabet, ord('a') = 0, ord('b') = 1, ... ord('z') = 25.

    Examples
    split_words("Hello world!") ➞ ["Hello", "world!"]
    split_words("Hello,world!") ➞ ["Hello", "world!"]
    split_words("abcdef") == 3
    """
    # Check for whitespace
    if any(c.isspace() for c in txt):
        return txt.split()
    
    # Check for commas
    if ',' in txt:
        return txt.split(',')

    # No whitespace or commas: count lower-case letters with odd alphabetical index
    count = 0
    for ch in txt:
        if 'a' <= ch <= 'z':
            # ord('a') = 0, ord('b') = 1, ..., ord('z') = 25
            if (ord(ch) - ord('a')) % 2 == 1:
                count += 1
    return count

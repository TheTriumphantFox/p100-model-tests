def split_words(txt):
    """
    Given a string of words, return a list of words split on whitespace, if no whitespaces exists in the text you
    should split on commas ',' if no commas exists you should return the number of lower-case letters with odd order in the
    alphabet, ord('a') = 0, ord('b') = 1, ... ord('z') = 25
    Examples
    split_words("Hello world!") ➞ ["Hello", "world!"]
    split_words("Hello,world!") ➞ ["Hello", "world!"]
    split_words("abcdef") == 3
    """
    # If there is any whitespace, split on whitespace
    if any(c.isspace() for c in txt):
        return txt.split()
    # If there is a comma, split on commas
    if ',' in txt:
        return txt.split(',')
    # Otherwise count lower-case letters with odd order
    count = 0
    for ch in txt:
        if 'a' <= ch <= 'z':
            if (ord(ch) - ord('a')) % 2 == 1:
                count += 1
    return count

def is_happy(s: str) -> bool:
    """
    Return True if the string s is "happy", otherwise False.
    A string is happy if its length is at least 3 and every
    three consecutive characters are all distinct.
    """
    if len(s) < 3:
        return False

    for i in range(len(s) - 2):
        a, b, c = s[i], s[i + 1], s[i + 2]
        if a == b or a == c or b == c:
            return False
    return True

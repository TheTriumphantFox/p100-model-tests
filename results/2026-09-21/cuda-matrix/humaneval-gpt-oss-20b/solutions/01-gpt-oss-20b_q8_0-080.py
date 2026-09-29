def is_happy(s: str) -> bool:
    """
    Return True if the string s is "happy" according to the following rules:
    - The length of s must be at least 3.
    - For every group of three consecutive characters in s, the three characters must be distinct.
    """
    if len(s) < 3:
        return False

    for i in range(len(s) - 2):
        a, b, c = s[i], s[i + 1], s[i + 2]
        if a == b or a == c or b == c:
            return False
    return True

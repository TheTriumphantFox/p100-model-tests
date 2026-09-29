def cycpattern_check(a, b):
    """Return True if any rotation of b is a substring of a.

    Examples:
        cycpattern_check("abcd", "abd") -> False
        cycpattern_check("hello", "ell") -> True
        cycpattern_check("whassup", "psus") -> False
        cycpattern_check("abab", "baa") -> True
        cycpattern_check("efef", "eeff") -> False
        cycpattern_check("himenss", "simen") -> True
    """
    if not b:
        return True
    doubled = b + b
    for i in range(len(b)):
        rotation = doubled[i:i + len(b)]
        if rotation in a:
            return True
    return False

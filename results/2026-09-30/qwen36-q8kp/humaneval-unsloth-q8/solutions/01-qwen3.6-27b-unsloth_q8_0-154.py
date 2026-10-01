def cycpattern_check(a , b):
    """You are given 2 words. You need to return True if the second word or any of its rotations is a substring in the first word
    cycpattern_check("abcd","abd") => False
    cycpattern_check("hello","ell") => True
    cycpattern_check("whassup","psus") => False
    cycpattern_check("abab","baa") => True
    cycpattern_check("efef","eeff") => False
    cycpattern_check("himenss","simen") => True

    """
    if not b:
        return True
    # Generate all rotations of b
    n = len(b)
    rotations = set()
    for i in range(n):
        rotation = b[i:] + b[:i]
        rotations.add(rotation)
    # Check if any rotation is a substring of a
    for rot in rotations:
        if rot in a:
            return True
    return False

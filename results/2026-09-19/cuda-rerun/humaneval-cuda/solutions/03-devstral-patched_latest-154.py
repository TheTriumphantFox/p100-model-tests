def cycpattern_check(a, b):
    """You are given 2 words. You need to return True if the second word or any of its rotations is a substring in the first word"""
    if not b:
        return True
    len_b = len(b)
    doubled_b = b + b
    for i in range(len_b):
        rotation = doubled_b[i:i+len_b]
        if rotation in a:
            return True
    return False

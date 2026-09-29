def encrypt(s: str) -> str:
    """
    Encrypts a string by rotating each lowercase alphabetic character
    forward by 4 positions (a Caesar cipher with a shift of 4).
    Non‑alphabetic characters are left unchanged.
    """
    result = []
    shift = 4
    for ch in s:
        if 'a' <= ch <= 'z':
            # Compute new character with wrap‑around
            new_ord = ord('a') + (ord(ch) - ord('a') + shift) % 26
            result.append(chr(new_ord))
        else:
            result.append(ch)
    return ''.join(result)

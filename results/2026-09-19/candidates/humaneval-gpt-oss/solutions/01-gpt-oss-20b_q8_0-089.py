def encrypt(s: str) -> str:
    """
    Encrypts a string by shifting each lowercase alphabetic character
    forward by 4 positions (wrapping around from 'z' to 'a').
    Non-alphabetic characters are left unchanged.
    """
    result = []
    for ch in s:
        if 'a' <= ch <= 'z':
            # shift by 4 with wrap-around
            shifted = chr((ord(ch) - ord('a') + 4) % 26 + ord('a'))
            result.append(shifted)
        else:
            result.append(ch)
    return ''.join(result)

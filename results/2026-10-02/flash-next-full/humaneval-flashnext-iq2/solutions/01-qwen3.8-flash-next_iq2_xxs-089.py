def encrypt(s):
    """Create a function encrypt that takes a string as an argument and
    returns a string encrypted with the alphabet being rotated. 
    The alphabet should be rotated in a manner such that the letters 
    shift down by two multiplied to two places.
    For example:
    encrypt('hi') returns 'lm'
    encrypt('asdfghjkl') returns 'ewhjklnop'
    encrypt('gf') returns 'kj'
    encrypt('et') returns 'ix'
    """
    # The shift is 2 * 2 = 4 places
    shift = 4
    result = []
    for char in s:
        if char.isalpha():
            # Determine the base ASCII value (uppercase or lowercase)
            base = ord('A') if char.isupper() else ord('a')
            # Shift the character by the given amount
            shifted = chr((ord(char) - base + shift) % 26 + base)
            result.append(shifted)
        else:
            result.append(char)
    return ''.join(result)

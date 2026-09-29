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
    result = []
    for char in s:
        if char.isalpha():
            shift = 4  # 2 multiplied by 2
            if char.islower():
                base = ord('a')
            else:
                base = ord('A')
            original_pos = ord(char) - base
            new_pos = (original_pos + shift) % 26
            new_char = chr(base + new_pos)
            result.append(new_char)
        else:
            result.append(char)
    return ''.join(result)

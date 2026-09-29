from typing import List

def string_xor(a: str, b: str) -> str:
    """ Input are two strings a and b consisting only of 1s and 0s.
    Perform binary XOR on these inputs and return result also as a string.
    >>> string_xor('010', '110')
    '100'
    """
    # Ensure both strings have the same length by padding the shorter one with leading zeros
    max_len = max(len(a), len(b))
    a = a.zfill(max_len)
    b = b.zfill(max_len)
    
    result = []
    for bit_a, bit_b in zip(a, b):
        # XOR the bits: 1 XOR 1 = 0, 0 XOR 0 = 0, 1 XOR 0 = 1, 0 XOR 1 = 1
        xor_bit = '1' if bit_a != bit_b else '0'
        result.append(xor_bit)
    
    return ''.join(result)

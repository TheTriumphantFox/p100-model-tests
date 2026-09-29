def encode_cyclic(s: str) -> str:
    """
    Returns encoded string by cycling groups of three characters.
    """
    # split string into groups of length 3
    groups = [s[(3 * i):min((3 * i + 3), len(s))] for i in range((len(s) + 2) // 3)]
    # cycle elements in each group unless group has fewer than 3 characters
    groups = [(group[1:] + group[0]) if len(group) == 3 else group for group in groups]
    return "".join(groups)


def decode_cyclic(s: str) -> str:
    """
    Takes as input a string encoded with encode_cyclic and returns the original string.
    """
    # split string into groups of length 3
    groups = [s[(3 * i):min((3 * i + 3), len(s))] for i in range((len(s) + 2) // 3)]
    # reverse the cycle: move first character to the end
    groups = [(group[1:] + group[0]) if len(group) == 3 else group for group in groups]
    # Since encode_cyclic shifts left, decoding shifts right
    # For groups of length 3, shift right by one
    decoded_groups = [group[-1] + group[:-1] if len(group) == 3 else group for group in groups]
    return "".join(decoded_groups)

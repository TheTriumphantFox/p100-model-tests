import re

def anti_shuffle(s: str) -> str:
    """
    Return a string where each word (separated by whitespace) has its
    characters sorted in ascending ASCII order, while preserving the
    original whitespace and word order.

    Parameters
    ----------
    s : str
        Input string.

    Returns
    -------
    str
        The transformed string.
    """
    # Split the string into tokens that are either whitespace or non-whitespace.
    tokens = re.split(r'(\s+)', s)
    result_parts = []

    for token in tokens:
        if token.isspace() or token == '':
            # Preserve whitespace exactly as it appears.
            result_parts.append(token)
        else:
            # Sort the characters of the word.
            sorted_word = ''.join(sorted(token))
            result_parts.append(sorted_word)

    return ''.join(result_parts)

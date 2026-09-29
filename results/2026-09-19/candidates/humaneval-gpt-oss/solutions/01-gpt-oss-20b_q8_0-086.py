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
        The "anti‑shuffled" string.
    """
    # Split the string into tokens that are either whitespace or non‑whitespace.
    tokens = re.split(r'(\s+)', s)
    # Sort characters of each non‑whitespace token.
    sorted_tokens = [
        ''.join(sorted(tok)) if not tok.isspace() else tok
        for tok in tokens
    ]
    return ''.join(sorted_tokens)

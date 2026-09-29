import re

def is_bored(S: str) -> int:
    """
    Count the number of sentences that start with the word "I".
    Sentences are delimited by '.', '?' or '!'.

    Parameters
    ----------
    S : str
        A string containing one or more sentences.

    Returns
    -------
    int
        The number of sentences that start with "I".

    Examples
    --------
    >>> is_bored("Hello world")
    0
    >>> is_bored("The sky is blue. The sun is shining. I love this weather")
    1
    """
    # Split the string into sentences using the delimiters.
    # The regex captures the delimiter to keep it as a separate token,
    # but we only need the sentence text.
    sentences = re.split(r'[.!?]', S)
    count = 0
    for sentence in sentences:
        # Strip leading/trailing whitespace
        stripped = sentence.strip()
        if not stripped:
            continue
        # Check if the first word is exactly "I"
        first_word = stripped.split()[0]
        if first_word == "I":
            count += 1
    return count

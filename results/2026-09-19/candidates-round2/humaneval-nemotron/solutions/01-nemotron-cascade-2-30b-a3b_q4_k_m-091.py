def is_bored(S):
    """
    Count the number of sentences that start with the word "I".
    Sentences are delimited by '.', '?', or '!'.

    Parameters:
        S (str): Input string containing one or more sentences.

    Returns:
        int: Number of sentences that start with the word "I".
    """
    # Split the string into sentences using the delimiters '.', '?', '!'
    # The split will include empty strings if there are consecutive delimiters,
    # so we filter them out.
    import re
    sentences = re.split(r'[.!?]', S)
    count = 0
    for sentence in sentences:
        # Strip leading and trailing whitespace
        stripped = sentence.strip()
        if not stripped:
            continue  # Skip empty sentences
        # Check if the sentence starts with the word "I"
        # We need to ensure that "I" is a whole word at the beginning.
        # Split the sentence into words and check the first word.
        words = stripped.split()
        if words and words[0] == "I":
            count += 1
    return count

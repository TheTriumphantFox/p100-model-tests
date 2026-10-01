def is_bored(S):
    """
    You'll be given a string of words, and your task is to count the number
    of boredoms. A boredom is a sentence that starts with the word "I".
    Sentences are delimited by '.', '?' or '!'.
   
    For example:
    >>> is_bored("Hello world")
    0
    >>> is_bored("The sky is blue. The sun is shining. I love this weather")
    1
    """
    import re
    
    # Split the string into sentences by '.', '?' or '!'
    # We need to keep track of sentence boundaries
    sentences = re.split(r'[.?!]', S)
    
    count = 0
    for sentence in sentences:
        # Strip leading whitespace
        stripped = sentence.lstrip()
        if not stripped:
            continue
        # Check if the sentence starts with "I" followed by a non-alphanumeric character or end of string
        # The word "I" should be a standalone word
        # Check if it starts with "I" and then either ends or has a non-letter character
        if stripped.startswith('I'):
            # Make sure "I" is a complete word
            if len(stripped) == 1:
                count += 1
            elif not stripped[1].isalpha():
                count += 1
    
    return count

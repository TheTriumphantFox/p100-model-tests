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
        if stripped:
            # Check if the sentence starts with "I"
            # The word "I" should be followed by a space or be the entire sentence
            words = stripped.split()
            if words and words[0] == "I":
                count += 1
    
    return count

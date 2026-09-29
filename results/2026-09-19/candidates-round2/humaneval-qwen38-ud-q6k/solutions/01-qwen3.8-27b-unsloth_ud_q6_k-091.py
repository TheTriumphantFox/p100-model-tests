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
    # Split the string into sentences based on '.', '?' or '!'
    # We need to keep the delimiters to properly split, but we can use regex to split
    # and then check each sentence.
    
    # Split by sentence delimiters, keeping track of the sentences
    # Use regex to split, but we need to handle the case where the string ends without a delimiter
    sentences = re.split(r'[.?!]', S)
    
    count = 0
    for sentence in sentences:
        # Strip whitespace from the sentence
        stripped = sentence.strip()
        if stripped:
            # Check if the sentence starts with "I" as a whole word
            # We need to ensure it's the word "I" and not part of another word
            # Since we stripped, we can check if the first word is "I"
            words = stripped.split()
            if words and words[0] == "I":
                count += 1
    
    return count

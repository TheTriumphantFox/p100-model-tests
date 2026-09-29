import re

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
    # Split the string into sentences based on delimiters '.', '?' or '!'
    sentences = re.split(r'[.?!]', S)
    
    count = 0
    for sentence in sentences:
        # Strip whitespace and check if the sentence starts with "I"
        if sentence.strip().startswith("I"):
            count += 1
            
    return count

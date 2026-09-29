def encode(message):
    """
    Write a function that takes a message, and encodes in such a 
    way that it swaps case of all letters, replaces all vowels in 
    the message with the letter that appears 2 places ahead of that 
    vowel in the english alphabet. 
    Assume only letters. 
    
    Examples:
    >>> encode('test')
    'TGST'
    >>> encode('This is a message')
    'tHKS KS C MGSSCGG'
    """
    vowels = 'aeiouAEIOU'
    result = []
    for char in message:
        if char in vowels:
            # Find the position of the vowel in the alphabet
            # We need to handle both upper and lower case
            lower_char = char.lower()
            # Find the index of the vowel in 'aeiou'
            vowel_index = 'aeiou'.index(lower_char)
            # The vowel that appears 2 places ahead
            # a -> c, e -> g, i -> k, o -> q, u -> w
            replacement = 'cgkqw'[vowel_index]
            # Swap case: if original was upper, make lower; if lower, make upper
            if char.isupper():
                result.append(replacement.lower())
            else:
                result.append(replacement.upper())
        else:
            # Swap case
            if char.isupper():
                result.append(char.lower())
            else:
                result.append(char.upper())
    return ''.join(result)

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
    vowels = set('aeiouAEIOU')
    result = []
    for char in message:
        if char in vowels:
            # Determine the vowel's case
            if char.islower():
                # Find the vowel 2 places ahead in lowercase
                idx = 'aeiou'.index(char)
                new_char = 'aeiou'[idx + 2]
                # Swap case: since original was lower, new should be upper
                result.append(new_char.upper())
            else:
                # Find the vowel 2 places ahead in uppercase
                idx = 'AEIOU'.index(char)
                new_char = 'AEIOU'[idx + 2]
                # Swap case: since original was upper, new should be lower
                result.append(new_char.lower())
        else:
            # Just swap case
            if char.islower():
                result.append(char.upper())
            else:
                result.append(char.lower())
    return ''.join(result)

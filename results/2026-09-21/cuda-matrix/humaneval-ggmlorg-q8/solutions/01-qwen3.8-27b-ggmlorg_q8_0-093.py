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
            # Find the index in the alphabet
            idx = ord(lower_char) - ord('a')
            # Move 2 places ahead
            new_idx = (idx + 2) % 26
            new_char = chr(ord('a') + new_idx)
            # Swap case: if original was upper, make lower; if lower, make upper
            if char.isupper():
                new_char = new_char.upper()
            else:
                new_char = new_char.lower()
            result.append(new_char)
        else:
            # Swap case
            if char.isupper():
                result.append(char.lower())
            else:
                result.append(char.upper())
    return ''.join(result)

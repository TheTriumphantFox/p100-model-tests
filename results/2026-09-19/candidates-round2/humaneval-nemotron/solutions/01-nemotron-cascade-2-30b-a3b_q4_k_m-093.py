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
    vowels = "aeiouAEIOU"
    result = []
    for ch in message:
        if ch.lower() in vowels:
            # Find the position of the vowel in the alphabet (case-insensitive)
            pos = ord(ch.lower()) - ord('a')
            # Compute the new position (2 places ahead, wrap around if needed)
            new_pos = (pos + 2) % 26
            # Determine the case for the replacement character
            if ch.isupper():
                new_ch = chr(ord('A') + new_pos)
            else:
                new_ch = chr(ord('a') + new_pos)
            result.append(new_ch)
        else:
            # Swap the case of the current character
            result.append(ch.swapcase())
    return ''.join(result)

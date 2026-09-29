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
            # Find the vowel's position in the alphabet (case-insensitive)
            lower_char = char.lower()
            # Get the letter 2 places ahead in the alphabet
            new_char = chr((ord(lower_char) - ord('a') + 2) % 26 + ord('a'))
            # Swap case: if original was uppercase, make new char lowercase, and vice versa
            if char.isupper():
                result.append(new_char.lower())
            else:
                result.append(new_char.upper())
        else:
            # Swap case for non-vowels
            if char.isupper():
                result.append(char.lower())
            else:
                result.append(char.upper())
    return ''.join(result)

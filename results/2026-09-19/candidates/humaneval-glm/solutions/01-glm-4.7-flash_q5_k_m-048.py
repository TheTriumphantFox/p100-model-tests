def is_palindrome(text: str):
    """
    Checks if given string is a palindrome
    >>> is_palindrome('')
    True
    >>> is_palindrome('aba')
    True
    >>> is_palindrome('aaaaa')
    True
    >>> is_palindrome('zbcd')
    False
    """
    # Normalize the string by removing non-alphanumeric characters and converting to lowercase
    # This handles cases like "A man, a plan, a canal: Panama"
    cleaned_text = ''.join(char.lower() for char in text if char.isalnum())
    
    # Check if the cleaned string reads the same forwards and backwards
    return cleaned_text == cleaned_text[::-1]

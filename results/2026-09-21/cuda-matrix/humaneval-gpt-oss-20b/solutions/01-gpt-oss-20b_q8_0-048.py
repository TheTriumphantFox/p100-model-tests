def is_palindrome(text: str) -> bool:
    """
    Checks if given string is a palindrome.

    The check is case-sensitive and considers all characters, including
    whitespace and punctuation.

    >>> is_palindrome('')
    True
    >>> is_palindrome('aba')
    True
    >>> is_palindrome('aaaaa')
    True
    >>> is_palindrome('zbcd')
    False
    """
    return text == text[::-1]

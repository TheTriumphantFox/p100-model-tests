def is_palindrome(string: str) -> bool:
    """ Test if given string is a palindrome """
    return string == string[::-1]


def make_palindrome(string: str) -> str:
    """ Find the shortest palindrome that begins with a supplied string.
    Algorithm idea is simple:
    - Find the longest postfix of supplied string that is a palindrome.
    - Append to the end of the string reverse of a string prefix that comes before the palindromic suffix.
    >>> make_palindrome('')
    ''
    >>> make_palindrome('cat')
    'catac'
    >>> make_palindrome('cata')
    'catac'
    """
    if not string:
        return ''
    
    n = len(string)
    # Find the longest postfix that is a palindrome
    # A postfix starting at index i means string[i:] is a palindrome
    # We want the longest such postfix, so we start from i=0 and go up
    for i in range(n):
        if is_palindrome(string[i:]):
            # The prefix before this palindromic suffix is string[:i]
            # We need to append the reverse of this prefix to the end
            prefix = string[:i]
            return string + prefix[::-1]
    
    # Fallback (shouldn't reach here for non-empty string since single char is palindrome)
    return string + string[:-1][::-1]

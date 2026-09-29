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
    
    # Find the longest suffix of string that is a palindrome
    n = len(string)
    # Check from the full string down to length 1
    for i in range(n):
        suffix = string[i:]
        if is_palindrome(suffix):
            # The prefix before this suffix is string[:i]
            # We need to append the reverse of this prefix to the end
            prefix = string[:i]
            return string + prefix[::-1]
    
    # This should never happen because a single character is always a palindrome
    return string + string[:-1][::-1]

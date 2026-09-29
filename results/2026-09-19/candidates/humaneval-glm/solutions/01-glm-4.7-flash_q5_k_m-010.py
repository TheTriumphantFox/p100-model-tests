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
        return string

    # Find the longest suffix that is a palindrome
    # We iterate from the end of the string towards the beginning
    for i in range(len(string)):
        suffix = string[i:]
        if is_palindrome(suffix):
            # The prefix is everything before the palindrome suffix
            prefix = string[:i]
            # The palindrome is the original string + reverse of the prefix
            return string + prefix[::-1]

    # Fallback (should theoretically never be reached for non-empty strings)
    return string + string[::-1]

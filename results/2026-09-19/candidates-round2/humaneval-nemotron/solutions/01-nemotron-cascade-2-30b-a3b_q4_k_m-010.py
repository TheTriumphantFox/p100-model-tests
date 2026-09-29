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
    n = len(string)
    # Find the longest suffix of `string` that is a palindrome.
    # We check suffixes starting from the full string down to length 1.
    for i in range(n, 0, -1):
        suffix = string[n - i:]
        if is_palindrome(suffix):
            # The part before this suffix is the prefix we need to mirror.
            prefix = string[:n - i]
            # Append the reverse of the prefix to the original string.
            return string + prefix[::-1]
    # If no palindromic suffix is found (should not happen because single characters are palindromes),
    # the whole string is treated as the prefix to mirror.
    return string + string[::-1]

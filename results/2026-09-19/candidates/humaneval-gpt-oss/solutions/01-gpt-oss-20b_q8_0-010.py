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
    # Find the longest palindromic suffix
    longest_suffix_len = 0
    for i in range(n + 1):
        suffix = string[i:]
        if is_palindrome(suffix):
            longest_suffix_len = n - i
            break  # first (longest) palindrome suffix found
    # The prefix that needs to be mirrored
    prefix = string[: n - longest_suffix_len]
    return string + prefix[::-1]

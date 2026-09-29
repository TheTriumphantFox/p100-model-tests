def flip_case(string: str) -> str:
    """For a given string, flip lowercase characters to uppercase and uppercase to lowercase.

    >>> flip_case('Hello')
    'hELLO'
    >>> flip_case('hELLO')
    'Hello'
    >>> flip_case('123')
    '123'
    >>> flip_case('')
    ''
    """
    return string.swapcase()

from typing import List


def separate_paren_groups(paren_string: str) -> List[str]:
    """Input to this function is a string containing multiple groups of nested parentheses.
    Separate those groups into separate strings and return the list of those.
    Separate groups are balanced (each open brace is properly closed) and not nested within each other.
    Ignore any spaces in the input string.

    >>> separate_paren_groups('( ) (( )) (( )( ))')
    ['()', '(())', '(()())']
    """
    groups: List[str] = []
    current: List[str] = []
    depth = 0

    for ch in paren_string:
        if ch == ' ':
            continue
        if ch == '(':
            if depth == 0:
                current = ['(']
            else:
                current.append('(')
            depth += 1
        elif ch == ')':
            depth -= 1
            current.append(')')
            if depth == 0:
                groups.append(''.join(current))
                current = []
        else:
            # ignore any other characters
            continue

    return groups

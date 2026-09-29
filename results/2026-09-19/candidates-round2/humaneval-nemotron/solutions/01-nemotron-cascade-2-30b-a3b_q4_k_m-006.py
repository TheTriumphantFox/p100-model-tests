from typing import List

def parse_nested_parens(paren_string: str) -> List[int]:
    """Input to this function is a string represented multiple groups for nested parentheses separated by spaces.
    For each of the group, output the deepest level of nesting of parentheses.
    E.g. (()()) has maximum two levels of nesting while ((())) has three.

    >>> parse_nested_parens('(()()) ((())) () ((())()())')
    [2, 3, 1, 3]
    """
    def max_depth(s: str) -> int:
        current = 0
        max_d = 0
        for ch in s:
            if ch == '(':
                current += 1
                if current > max_d:
                    max_d = current
            elif ch == ')':
                current -= 1
        return max_d

    groups = paren_string.split()
    return [max_depth(g) for g in groups]

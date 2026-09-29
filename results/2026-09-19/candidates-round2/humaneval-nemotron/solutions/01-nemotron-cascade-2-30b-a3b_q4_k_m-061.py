def correct_bracketing(brackets: str) -> bool:
    """Return True if every opening bracket has a corresponding closing bracket.

    The function checks that the string consists only of '(' and ')' and that
    each '(' is matched by a later ')'.  It returns False for any other
    situation (e.g., unmatched opening or closing brackets, or an empty
    string).

    >>> correct_bracketing("(")
    False
    >>> correct_bracketing("()")
    True
    >>> correct_bracketing("(()())")
    True
    >>> correct_bracketing(")(()")
    False
    """
    balance = 0
    for ch in brackets:
        if ch == '(':
            balance += 1
        elif ch == ')':
            balance -= 1
        else:
            # Invalid character encountered
            return False
        if balance < 0:
            # More closing than opening brackets at this point
            return False
    return balance == 0

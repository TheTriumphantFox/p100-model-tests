def correct_bracketing(brackets: str) -> bool:
    """
    Return True if every opening bracket '<' has a corresponding closing bracket '>'.
    The string consists only of '<' and '>' characters.

    >>> correct_bracketing("<")
    False
    >>> correct_bracketing("<>")
    True
    >>> correct_bracketing("<<><>>")
    True
    >>> correct_bracketing("><<>")
    False
    """
    balance = 0
    for ch in brackets:
        if ch == '<':
            balance += 1
        elif ch == '>':
            balance -= 1
            if balance < 0:
                return False
        else:
            # Invalid character; according to the problem statement this should not happen,
            # but we treat it as an error.
            return False
    return balance == 0

def correct_bracketing(brackets: str) -> bool:
    """
    brackets is a string of "<" and ">".
    return True if every opening bracket has a corresponding closing bracket.

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
        if ch == "<":
            balance += 1
        elif ch == ">":
            balance -= 1
        else:
            # ignore any other characters (should not appear per spec)
            continue
        if balance < 0:
            return False
    return balance == 0

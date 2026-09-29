def correct_bracketing(brackets: str) -> bool:
    """
    Return True if every opening bracket has a corresponding closing bracket.
    """
    balance = 0
    for ch in brackets:
        if ch == '(':
            balance += 1
        elif ch == ')':
            balance -= 1
            if balance < 0:
                return False
        else:
            # ignore any other characters (though spec says only '(' and ')')
            continue
    return balance == 0

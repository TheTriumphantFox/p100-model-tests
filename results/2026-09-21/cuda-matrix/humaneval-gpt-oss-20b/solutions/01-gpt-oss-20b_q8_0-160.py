def do_algebra(operator, operand):
    """
    Evaluate an arithmetic expression defined by a list of operators and operands.
    The operators are applied with normal Python precedence rules.
    """
    # Map operator symbols to themselves (they are already valid Python operators)
    valid_ops = {'+', '-', '*', '//', '**'}
    if not operator or not operand:
        raise ValueError("Operator and operand lists must not be empty.")
    if len(operator) != len(operand) - 1:
        raise ValueError("Number of operators must be one less than number of operands.")
    # Build the expression string
    expr_parts = []
    for op, val in zip(operator, operand):
        if op not in valid_ops:
            raise ValueError(f"Unsupported operator: {op}")
        expr_parts.append(str(val))
        expr_parts.append(op)
    expr_parts.append(str(operand[-1]))
    expr = "".join(expr_parts)
    # Evaluate safely using eval (only arithmetic operators are present)
    return eval(expr)

def answer(question):
    if not question.startswith("What is") or not question.endswith("?"):
        raise ValueError("unknown operation")

    # Remove "What is" prefix and "?" suffix
    body = question[7:-1].strip()
    
    if not body:
        raise ValueError("syntax error")

    # Normalize operations
    body = body.replace("multiplied by", "multiplied")
    body = body.replace("divided by", "divided")

    tokens = body.split()
    
    if not tokens:
        raise ValueError("syntax error")

    # Parse the first number
    try:
        result = int(tokens[0])
    except ValueError:
        raise ValueError("syntax error")

    i = 1
    while i < len(tokens):
        op = tokens[i]
        
        # Check if the operator is valid
        # If we expect an operator, but get a number, it's a syntax error
        try:
            int(op)
            raise ValueError("syntax error")
        except ValueError as e:
            if str(e) == "syntax error":
                raise

        if op not in ("plus", "minus", "multiplied", "divided"):
            raise ValueError("unknown operation")
        
        # Check if there is a number following the operator
        if i + 1 >= len(tokens):
            raise ValueError("syntax error")
        
        next_token = tokens[i + 1]
        try:
            operand = int(next_token)
        except ValueError:
            raise ValueError("syntax error")
        
        if op == "plus":
            result += operand
        elif op == "minus":
            result -= operand
        elif op == "multiplied":
            result *= operand
        elif op == "divided":
            result /= operand
        
        i += 2

    return result

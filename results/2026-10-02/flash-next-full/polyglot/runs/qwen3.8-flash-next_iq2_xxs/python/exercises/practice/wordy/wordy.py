def answer(question):
    if not question.startswith("What is ") or not question.endswith("?"):
        raise ValueError("unknown operation")
    
    expression = question[8:-1].strip()
    
    if not expression:
        raise ValueError("syntax error")

    tokens = expression.split()
    
    # Normalize multi-word operators to single tokens for easier parsing
    normalized_tokens = []
    i = 0
    while i < len(tokens):
        if i < len(tokens) - 1:
            if tokens[i] == "multiplied" and tokens[i+1] == "by":
                normalized_tokens.append("multiplied by")
                i += 2
                continue
            if tokens[i] == "divided" and tokens[i+1] == "by":
                normalized_tokens.append("divided by")
                i += 2
                continue
        normalized_tokens.append(tokens[i])
        i += 1
        
    tokens = normalized_tokens

    known_ops = {"plus", "minus", "multiplied by", "divided by"}
    
    # Check for unknown operations first
    for token in tokens:
        if token in known_ops:
            continue
        try:
            int(token)
        except ValueError:
            raise ValueError("unknown operation")

    if len(tokens) == 0:
        raise ValueError("syntax error")
        
    # Validate syntax: must start with number, end with number, alternate num/op
    for i, token in enumerate(tokens):
        try:
            int(token)
            is_num = True
        except ValueError:
            is_num = False
            
        if i % 2 == 0:
            if not is_num:
                raise ValueError("syntax error")
        else:
            if is_num:
                raise ValueError("syntax error")
            if token not in known_ops:
                raise ValueError("unknown operation")

    if len(tokens) == 0:
        raise ValueError("syntax error")

    result = int(tokens[0])
    for i in range(1, len(tokens), 2):
        op = tokens[i]
        try:
            num = int(tokens[i+1])
        except (IndexError, ValueError):
            raise ValueError("syntax error")
            
        if op == "plus":
            result += num
        elif op == "minus":
            result -= num
        elif op == "multiplied by":
            result *= num
        elif op == "divided by":
            if num == 0:
                raise ValueError("syntax error")
            result //= num
            
    return result

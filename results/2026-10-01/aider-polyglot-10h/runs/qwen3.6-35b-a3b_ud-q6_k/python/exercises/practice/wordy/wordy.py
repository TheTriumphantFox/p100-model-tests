def answer(question):
    if not question.startswith("What is"):
        raise ValueError("unknown operation")
    
    if not question.endswith("?"):
        raise ValueError("syntax error")
        
    question = question[7:-1].strip()
    
    if not question:
        raise ValueError("syntax error")

    # Replace words with symbols for easier parsing
    question = question.replace("plus", "+")
    question = question.replace("minus", "-")
    question = question.replace("multiplied by", "*")
    question = question.replace("divided by", "/")
    
    tokens = question.split()
    
    if not tokens:
        raise ValueError("syntax error")

    # The first token must be a number
    try:
        current_result = int(tokens[0])
    except ValueError:
        raise ValueError("syntax error")

    i = 1
    while i < len(tokens):
        op = tokens[i]
        
        if op not in ("+", "-", "*", "/"):
            # If it's a number, it's a syntax error (e.g. two numbers in a row)
            try:
                int(op)
                raise ValueError("syntax error")
            except ValueError:
                # It's not a number. It might be an unknown operation word
                # or just a random word.
                # If it looks like an operation word but wasn't replaced, it's unknown operation.
                # Otherwise it's a syntax error.
                raise ValueError("unknown operation")
            
        i += 1
        if i >= len(tokens):
            raise ValueError("syntax error")
            
        try:
            number = int(tokens[i])
        except ValueError:
            raise ValueError("syntax error")
            
        if op == "+":
            current_result += number
        elif op == "-":
            current_result -= number
        elif op == "*":
            current_result *= number
        elif op == "/":
            current_result /= number
            
        i += 1
        
    return int(current_result)

def answer(question):
    question = question.strip()
    if not question.endswith('?'):
        raise ValueError("syntax error")
    
    question = question[:-1]
    
    if not question.startswith("What is "):
        raise ValueError("syntax error")
        
    question = question[len("What is "):]
    
    tokens = question.split()
    
    if not tokens:
        raise ValueError("syntax error")
        
    try:
        current = int(tokens[0])
    except ValueError:
        raise ValueError("syntax error")
        
    i = 1
    while i < len(tokens):
        if i >= len(tokens):
            raise ValueError("syntax error")
            
        op = tokens[i]
        
        if op == "plus":
            if i + 1 >= len(tokens):
                raise ValueError("syntax error")
            try:
                num = int(tokens[i + 1])
            except ValueError:
                raise ValueError("syntax error")
            current += num
            i += 2
        elif op == "minus":
            if i + 1 >= len(tokens):
                raise ValueError("syntax error")
            try:
                num = int(tokens[i + 1])
            except ValueError:
                raise ValueError("syntax error")
            current -= num
            i += 2
        elif op == "multiplied":
            if i + 2 >= len(tokens) or tokens[i + 1] != "by":
                raise ValueError("syntax error")
            try:
                num = int(tokens[i + 2])
            except ValueError:
                raise ValueError("syntax error")
            current *= num
            i += 3
        elif op == "divided":
            if i + 2 >= len(tokens) or tokens[i + 1] != "by":
                raise ValueError("syntax error")
            try:
                num = int(tokens[i + 2])
            except ValueError:
                raise ValueError("syntax error")
            if num == 0:
                raise ValueError("syntax error")
            current //= num
            i += 3
        else:
            raise ValueError("unknown operation")
            
    return current

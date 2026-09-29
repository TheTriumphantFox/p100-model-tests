def is_nested(string):
    '''
    Create a function that takes a string as input which contains only square brackets.
    The function should return True if and only if there is a valid subsequence of brackets 
    where at least one bracket in the subsequence is nested.

    is_nested('[[]]') ➞ True
    is_nested('[]]]]]]][[[[[]') ➞ False
    is_nested('[][]') ➞ False
    is_nested('[]') ➞ False
    is_nested('[[][]]') ➞ True
    is_nested('[[]][[') ➞ True
    '''
    stack = []
    pairs = []  # stores (start, end) for valid matched pairs
    
    for i, ch in enumerate(string):
        if ch == '[':
            stack.append(i)
        elif ch == ']':
            if stack:
                start = stack.pop()
                pairs.append((start, i))
    
    # Check if any pair is nested inside another pair
    for i in range(len(pairs)):
        for j in range(len(pairs)):
            if i != j:
                s1, e1 = pairs[i]
                s2, e2 = pairs[j]
                # Pair i is nested inside pair j if s2 < s1 and e1 < e2
                if s2 < s1 and e1 < e2:
                    return True
    
    return False

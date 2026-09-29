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
    # We need to check if there exists a valid subsequence of brackets
    # where at least one bracket is nested (i.e., depth >= 2 at some point)
    
    # A valid subsequence means we can pick a subsequence of the string that forms
    # a valid bracket sequence. We want to know if there's such a subsequence
    # that has nesting depth at least 2.
    
    # Key insight: We can greedily try to form a valid bracket sequence with maximum nesting.
    # Actually, let's think differently.
    
    # We want to know if there exists a subsequence that is a valid bracket sequence
    # and has at least one pair of nested brackets.
    
    # A valid bracket sequence with nesting depth >= 2 must contain at least 4 brackets:
    # the outer pair and the inner pair.
    
    # Let's think about it this way: we need to find indices i < j < k < l such that
    # string[i] = '[', string[j] = '[', string[k] = ']', string[l] = ']'
    # This would form the subsequence "[[]]" which is valid and nested.
    
    # So the question reduces to: does the string contain a subsequence "[[]]"?
    
    # Let's check for the existence of such a subsequence.
    
    # We need to find:
    # 1. A '[' at some position
    # 2. A '[' after that
    # 3. A ']' after the second '['
    # 4. A ']' after the third character
    
    # Let's do this with a simple scan.
    
    n = len(string)
    if n < 4:
        return False
    
    # Find the first '['
    # Then find a '[' after it
    # Then find a ']' after that
    # Then find a ']' after that
    
    # Let's use a state machine approach:
    # State 0: looking for first '['
    # State 1: looking for second '['
    # State 2: looking for first ']'
    # State 3: looking for second ']'
    
    state = 0
    for ch in string:
        if state == 0:
            if ch == '[':
                state = 1
        elif state == 1:
            if ch == '[':
                state = 2
        elif state == 2:
            if ch == ']':
                state = 3
        elif state == 3:
            if ch == ']':
                return True
    
    return False

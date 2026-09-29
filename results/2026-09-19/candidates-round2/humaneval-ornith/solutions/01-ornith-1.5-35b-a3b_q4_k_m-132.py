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
    depth = 0
    max_depth = 0
    for char in string:
        if char == '[':
            depth += 1
            if depth > max_depth:
                max_depth = depth
        elif char == ']':
            if depth == 0:
                return False
            depth -= 1
    return max_depth >= 2 and depth == 0

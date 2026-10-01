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
    # We need to find if there exists a valid subsequence of brackets that has at least one nesting.
    # A valid bracket sequence is one where brackets are properly matched.
    # "Nested" means there's at least one pair of brackets inside another pair.
    # For example, '[[]]' has nesting because the inner [] is inside the outer [].
    # '[][]' does not have nesting because the two pairs are adjacent, not nested.
    
    # One approach: find the longest valid subsequence (or any valid subsequence) and check if it has nesting.
    # But actually, we just need to check if there exists ANY valid subsequence with nesting.
    
    # A simpler approach: scan through the string and track the depth of nesting in a valid bracket sequence.
    # We can use a stack-based approach to find valid bracket subsequences.
    
    # Actually, let's think about it differently. We want to know if there's a valid subsequence with nesting.
    # A valid subsequence with nesting means we can pick some brackets from the string such that they form a valid bracket sequence with at least one nested pair.
    
    # Key insight: If we can find two opening brackets such that there's a closing bracket after the first opening, and another closing bracket after the second opening (which is after the first opening), and the closings are in the right order... 
    
    # Let me think of a simpler approach:
    # We can iterate through the string and maintain a counter for the current depth of a valid bracket sequence.
    # If at any point the depth reaches 2 or more, that means we have nesting.
    
    # But we need to be careful: we're looking for a subsequence, not a substring. So we can skip characters.
    
    # Approach: Use a greedy method. Go through the string, and whenever we see an opening bracket, we increment a depth counter. When we see a closing bracket, if depth > 0, we decrement it. If at any point depth >= 2, we have found nesting.
    
    # Wait, but this checks for a valid prefix/subsequence. Let me reconsider.
    
    # Actually, the standard way to check for valid bracket sequences uses a stack or counter. For subsequences, we can greedily match.
    
    # Let's try: iterate through the string, keep a depth counter. For each '[' increment depth. For each ']', if depth > 0, decrement depth. If depth ever reaches 2, return True. If we finish and depth never reached 2, return False.
    
    depth = 0
    for char in string:
        if char == '[':
            depth += 1
            if depth >= 2:
                return True
        elif char == ']':
            if depth > 0:
                depth -= 1
    return False

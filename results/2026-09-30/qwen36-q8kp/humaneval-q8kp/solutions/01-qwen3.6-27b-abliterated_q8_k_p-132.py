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
    # We need to find if there exists a valid subsequence of brackets that has at least one nested bracket.
    # A valid bracket sequence is one where every opening bracket has a matching closing bracket in the correct order.
    # "Nested" means there is at least one pair of brackets inside another pair, e.g., [[]]
    
    # Approach: Use a stack to track opening brackets. We want to detect if there's any point where
    # we have a nested structure. One way: find if there's a valid subsequence with nesting depth >= 2.
    
    # Let's think differently: we need to find a subsequence (not necessarily contiguous) that forms
    # a valid bracket sequence with at least one nested pair.
    
    # A simpler approach: check if there exists a '[' that is followed (in the subsequence sense) by 
    # another '[' which is then followed by its matching ']' and then the outer ']'.
    
    # Actually, let's use a stack-based approach to find the maximum nesting depth of any valid subsequence.
    # But since it's a subsequence, we can pick and choose brackets.
    
    # Key insight: For a subsequence to be a valid bracket sequence with nesting, we need at least two 
    # opening brackets before any closing bracket in the subsequence.
    
    # Let's find if we can form a valid bracket sequence with depth >= 2.
    # We can greedily pick brackets: scan left to right, maintain a stack. When we see '[', push it.
    # When we see ']', if stack is non-empty, pop. Track the maximum depth reached.
    
    # But wait, for subsequences, we can skip characters. So the question becomes: what's the maximum
    # nesting depth of a valid bracket subsequence?
    
    # Actually, let me reconsider. The problem says "valid subsequence of brackets where at least one 
    # bracket in the subsequence is nested." This means the subsequence itself must be a valid bracket 
    # sequence, and within that sequence, there is nesting (depth >= 2).
    
    # To maximize nesting depth in a subsequence, we can use a greedy approach:
    # Count the number of '[' and ']' we can use. The maximum nesting depth of a valid bracket 
    # subsequence is limited by min(count of '[', count of ']'), but we need to ensure proper ordering.
    
    # Let me use a different approach: simulate building the deepest possible valid bracket subsequence.
    # Use a stack. Iterate through the string:
    # - If we see '[', push it onto the stack.
    # - If we see ']', and the stack is non-empty, pop from the stack (matching this ']' with the most recent '[').
    # Track the maximum size the stack ever reached. If max depth >= 2, return True.
    
    stack = []
    max_depth = 0
    for ch in string:
        if ch == '[':
            stack.append(ch)
            max_depth = max(max_depth, len(stack))
        elif ch == ']':
            if stack:
                stack.pop()
    
    return max_depth >= 2

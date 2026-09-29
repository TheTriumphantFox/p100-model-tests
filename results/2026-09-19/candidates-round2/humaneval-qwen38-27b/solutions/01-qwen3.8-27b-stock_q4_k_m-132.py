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
    
    # A valid subsequence means we can pick a subsequence of the string
    # that forms a valid bracket sequence with nesting.
    
    # Key insight: We need to find if there's a subsequence that is a valid
    # bracket sequence with at least one nested pair.
    
    # Let's think about it differently. We can use a greedy approach:
    # We want to see if we can form a valid bracket sequence with depth >= 2.
    
    # Actually, let's reconsider. The problem says "valid subsequence of brackets where at least one bracket in the subsequence is nested."
    
    # A bracket is nested if it's inside another bracket. So we need a valid bracket sequence of length >= 4 (at least [[]]) or similar.
    
    # Let's use a different approach: we can try to find if there exists a subsequence that is a valid bracket sequence with maximum depth >= 2.
    
    # We can use dynamic programming or a greedy method.
    
    # Greedy approach: 
    # We can try to build a valid bracket sequence by scanning the string.
    # We maintain a "depth" counter. When we see '[', we can choose to include it (increasing depth).
    # When we see ']', we can choose to include it (decreasing depth) if depth > 0.
    # We want to see if we can achieve depth >= 2 at any point while maintaining a valid sequence.
    
    # But we need to be careful: we're choosing a subsequence, so we can skip characters.
    
    # Let's think: we want to know if there's a subsequence that is a valid bracket sequence with max depth >= 2.
    
    # We can use a state machine approach. Let's define:
    # - We can be in a state where we've built a valid prefix of a bracket sequence.
    # - We track the current depth.
    
    # Actually, a simpler approach: 
    # We can try to find two '[' characters and two ']' characters such that the first '[' comes before the second '[', and the first ']' comes after the second '[', and the second ']' comes after the first ']'.
    # Wait, that's not quite right.
    
    # Let me think again. For a valid bracket sequence with nesting, we need at least:
    # [ [ ] ]
    # So we need to find indices i < j < k < l such that string[i] = '[', string[j] = '[', string[k] = ']', string[l] = ']'
    # But we also need to ensure that the subsequence is valid. If we pick these 4 characters in order, the subsequence is "[[]]" which is valid.
    
    # So the question reduces to: does there exist i < j < k < l such that string[i] = '[', string[j] = '[', string[k] = ']', string[l] = ']'?
    
    # Wait, but we could also have longer sequences. But if we can find such a pattern, that's sufficient.
    
    # Let's verify with the examples:
    # is_nested('[[]]') -> indices 0,1,2,3: '[','[',']',']' -> True
    # is_nested('[]]]]]]][[[[[]') -> Let's see: we need two '[' followed by two ']' in order.
    #   The string is: [ ] ] ] ] ] ] [ [ [ [ [ ]
    #   We need i < j < k < l with string[i]='[', string[j]='[', string[k]=']', string[l]=']'
    #   The '[' characters are at indices 0, 7, 8, 9, 10, 11
    #   The ']' characters are at indices 1, 2, 3, 4,

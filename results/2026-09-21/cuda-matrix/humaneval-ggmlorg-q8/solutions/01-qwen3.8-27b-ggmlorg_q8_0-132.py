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
    
    # Let's think about it this way: we can pick any subsequence. We want to know if
    # there's a valid bracket subsequence with depth >= 2.
    
    # One approach: try to find if we can form a valid bracket sequence with depth >= 2.
    # We can use a greedy approach: scan through the string, and try to build a valid
    # bracket sequence while tracking the maximum depth.
    
    # Actually, let's think more carefully. We can pick any subsequence. So we want to
    # know if there exist indices i < j < k < l such that s[i] = '[', s[j] = '[', s[k] = ']', s[l] = ']'
    # and the subsequence s[i], s[j], s[k], s[l] is a valid bracket sequence.
    
    # For s[i], s[j], s[k], s[l] to be a valid bracket sequence, we need:
    # s[i] = '[', s[j] = '[', s[k] = ']', s[l] = ']'
    # And the sequence "[[]]" is valid.
    
    # So the question reduces to: does there exist i < j < k < l such that
    # s[i] = '[', s[j] = '[', s[k] = ']', s[l] = ']'?
    
    # Wait, that's not quite right. The subsequence doesn't have to be exactly 4 characters.
    # But if there's a valid subsequence with depth >= 2, then it must contain at least
    # one instance of "[[]]" as a subsequence (not necessarily contiguous).
    
    # Actually, any valid bracket sequence with depth >= 2 contains "[[]]" as a subsequence.
    # Because if the depth reaches 2, there must be two opening brackets before any closing
    # bracket that brings the depth back to 1, and then a closing bracket.
    
    # So we just need to check if "[[]]" is a subsequence of the string.
    
    # Let's verify with the examples:
    # is_nested('[[]]') -> "[[]]" is a subsequence of "[[]]" -> True ✓
    # is_nested('[]]]]]]][[[[[]') -> Let's check: we need '[', '[', ']', ']' in order.
    #   The string is: [ ] ] ] ] ] ] [ [ [ [ [ ]
    #   First '[' at index 0. Then we need another '[' after index 0. The next '[' is at index 7.
    #   Then we need ']' after index 7. The next ']' is at index 12.
    #   Then we need ']' after index 12. There's no ']' after index 12. So False ✓
    # is_nested('[][]') -> We need '[', '[', ']', ']' in order.
    #   First '[' at index 0. Next '[' at index 2. Next ']' after index 2 is at index 3.
    #   Next ']' after index 3: none. So False ✓
    # is_nested('[]') ->

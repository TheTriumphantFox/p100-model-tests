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
    # We need to find if there exists a valid bracket subsequence that has at least one nested pair.
    # A valid bracket subsequence is one that can be formed by deleting some characters (not necessarily contiguous)
    # such that the resulting string is a valid bracket sequence (balanced and properly nested).
    # And within that valid subsequence, there must be at least one pair of brackets that are nested,
    # i.e., there exists some '[' followed later by ']' with at least one other pair inside them.
    # Equivalently, the valid subsequence must contain "[[...]]" pattern (two opening brackets before a closing one).
    
    # Approach: We can greedily build the longest valid bracket subsequence by scanning left to right,
    # keeping track of unmatched opening brackets. But we need to know if we can form a valid subsequence
    # that has nesting depth >= 2.
    
    # Actually, we just need to check if there exists a valid bracket subsequence with depth >= 2.
    # This is equivalent to: can we find two '[' that are both matched with ']' later, such that
    # the first '[' is matched with a ']' that comes after the second '[' is matched with its ']'.
    # In other words, there exist indices i < j < k < l with string[i] == '[' and string[j] == '[' and string[k] == ']' and string[l] == ']'.
    # And these four brackets can be part of a valid subsequence (which they can if we just take them and ignore others).
    # But we also need the whole subsequence to be valid. If we just take those four brackets, they form "[[]]" which is valid.
    # So the condition reduces to: does there exist a subsequence "[[]]" in the string?
    # Wait, is that sufficient? If we have "[[]]" as a subsequence, then we can take that as our valid subsequence,
    # and it has nesting (the inner pair is nested inside the outer pair). So yes.
    # But what if the string has "[[]]" as a subsequence but we can't form a valid full subsequence containing it?
    # Actually, if "[[]]" is a subsequence, we can just take that as our valid subsequence (it's already valid and has nesting).
    # So the problem reduces to: does the string contain "[[]]" as a subsequence?
    
    # Let's verify with examples:
    # '[[]]' -> contains "[[]]" as subsequence? Yes (the whole string). True. ✓
    # '[]]]]]]][[[[[]' -> does it contain "[[]]"? We need two '[' then two ']'. We have '[' at start, then ']'... but we need two '[' before two ']'. The string starts with '[]]...' so we have one '[', then ']', then more ']', then later '[[[[]' has three '[' then one ']'. So we can pick first '[' and then two '[' from the end and two ']'? We need order: '[' '[' ']' ']'. We have '[' at index 0, then '[' at some later index (from the '[[[[]' part), then ']' at index 1 (before the later '['), wait order matters: we need first '[' then second '[' then first ']' then second ']'. The first ']' is at index 1, which is before the later '['. So we can't use it after the second '['. We need two ']' after the second '['. The later part has '[[[[]' which has one ']' at the very end. So only one ']' after the second '['. So no "[[]]" subsequence. False. ✓
    # '[][]' -> does it contain "[[]]"? We need two '[' then two ']'. We have '[', ']', '[', ']'. Only one '[' before the first ']'? Actually we have '[' at 0, ']'

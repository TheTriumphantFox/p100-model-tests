def reverse_delete(s, c):
    """
    We are given two strings s and c, you have to delete all the characters in s that are equal to any character in c
    then check if the result string is a palindrome.
    A string is called palindrome if it reads the same backward as forward.
    You should return a tuple containing the result string and True/False for the check.

    Example
    For s = "abcde", c = "ae", the result should be ('bcd', False)
    For s = "abcdef", c = "b",  the result should be ('acdef', False)
    For s = "abcdedcba", c = "ab", the result should be ('cdedc', True)
    """
    # Build a set of characters to delete for O(1) lookups
    delete_set = set(c)
    # Filter out characters from s that are in the delete set
    result = ''.join(ch for ch in s if ch not in delete_set)
    # Check palindrome (case-sensitive)
    is_pal = result == result[::-1]
    return (result, is_pal)

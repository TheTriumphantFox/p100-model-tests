def check_if_last_char_is_a_letter(txt):
    '''
    Create a function that returns True if the last character
    of a given string is an alphabetical character and is not
    a part of a word, and False otherwise.
    Note: "word" is a group of characters separated by space.

    Examples:
    check_if_last_char_is_a_letter("apple pie") ➞ False
    check_if_last_char_is_a_letter("apple pi e") ➞ True
    check_if_last_char_is_a_letter("apple pi e ") ➞ False
    check_if_last_char_is_a_letter("") ➞ False 
    '''
    if not txt:
        return False
    
    # Strip trailing whitespace to find the actual last character
    stripped = txt.rstrip()
    
    if not stripped:
        return False
    
    last_char = stripped[-1]
    
    # Check if the last character is an alphabetical letter
    if not last_char.isalpha():
        return False
    
    # Check if it's a standalone word (preceded by space or start of string)
    if len(stripped) == 1:
        return True
    
    # The character before the last one should be a space
    return stripped[-2] == ' '

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
    stripped = txt.rstrip()
    if not stripped:
        return False
    last_char = stripped[-1]
    if not last_char.isalpha():
        return False
    # The last character must be a standalone word (not part of a longer word)
    if len(stripped) == 1:
        return True
    prev_char = stripped[-2]
    if prev_char == ' ':
        return True
    return False

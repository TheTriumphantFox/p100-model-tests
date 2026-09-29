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
    
    # The last character must be an alphabetical character
    last_char = txt[-1]
    if not last_char.isalpha():
        return False
    
    # The last character must not be part of a word.
    # A word is a group of characters separated by space.
    # So if the last character is a letter, it's part of a word unless it's a single-letter word.
    # But wait: "apple pi e" -> last char is 'e', which is a single-letter word, so True.
    # "apple pie" -> last char is 'e', which is part of "pie", so False.
    # "apple pi e " -> last char is ' ', not alpha, so False.
    
    # So we need to check: is the last character a letter, AND is it a single-letter word?
    # That means: the character before it (if exists) must be a space, OR it's the first character.
    # But also, the last character must be a letter.
    
    # Let's think: the last character is at index -1.
    # For it to be a single-letter word, either:
    # 1. It's the only character in the string (len == 1), or
    # 2. The character before it is a space.
    
    if len(txt) == 1:
        return last_char.isalpha()
    
    # Check if the character before the last is a space
    if txt[-2] == ' ':
        return last_char.isalpha()
    
    return False

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
    
    # Check if the last character is not part of a word
    # A word is a group of characters separated by space
    # So the last character is not part of a word if it is preceded by a space
    # or if it is the only character (but then it would be a word of length 1)
    # Wait, let's think about this more carefully.
    
    # "apple pie" -> last char 'e', preceded by 'i', so it's part of the word "pie" -> False
    # "apple pi e" -> last char 'e', preceded by ' ', so it's a standalone word "e" -> True
    # "apple pi e " -> last char ' ', not alpha -> False
    # "" -> False
    
    # So the condition is: the last character is alpha, AND the character before it is a space (or it's the first character)
    # But wait, if it's the first character, then it's a word of length 1. Is that "part of a word"? 
    # The problem says "not a part of a word". A single character is a word. So if the string is "a", the last char 'a' is part of the word "a". So it should return False?
    
    # Let me re-read: "returns True if the last character of a given string is an alphabetical character and is not a part of a word"
    
    # Hmm, "not a part of a word" is a bit ambiguous. Let me look at the examples again.
    # "apple pi e" -> True. Here 'e' is a standalone word. So it IS a word, but the function returns True.
    # So maybe "not a part of a word" means it's not part of a longer word? Or maybe it means it's a word by itself?
    
    # Actually, I think the intended meaning is: the last character is an alpha char, and it is a standalone word (i.e., preceded by a space or is the only character).
    
    # Let's check: if txt is "a", last char is 'a', it's alpha. Is it "not a part of a word"? It IS a word. So should it be False?
    # But the example "apple pi e" returns True where 'e' is a word.
    
    # I think the key is: the last character should be an alpha char, and the character immediately before it should be a space (or it should be the first character).
    
    if len(txt) == 1:
        # Single character, it's a word by itself. Based on the pattern, I think this should be True? 
        # But wait, let me reconsider. The problem says "not a part of a word". A single char is a word, so it IS part of a word (itself). 
        # Hmm, this is confusing. Let me just go with: preceded by space or is first char.
        return True
    
    # Check if the character before the last one is a space
    if txt[-2] == ' ':
        return True
    else:
        return False

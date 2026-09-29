def check_if_last_char_is_a_letter(txt):
    """
    Returns True if the last character of the string is an alphabetical character
    and is not part of a word (i.e., it is the only character after the final space),
    otherwise returns False.

    A "word" is defined as a group of characters separated by spaces.
    """
    # Return False for empty string
    if not txt:
        return False

    # Strip trailing spaces to find the actual last character
    stripped = txt.rstrip()
    if not stripped:
        return False

    last_char = stripped[-1]

    # Check if the last character is alphabetical
    if not last_char.isalpha():
        return False

    # Determine if the last character is part of a word
    # It is part of a word if there is a non-space character before it
    # (i.e., it is not the only character after the final space)
    if len(stripped) > 1 and stripped[-2] != ' ':
        return False

    return True

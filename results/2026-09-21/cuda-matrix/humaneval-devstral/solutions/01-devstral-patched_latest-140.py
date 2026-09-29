def fix_spaces(text):
    """
    Given a string text, replace all spaces in it with underscores,
    and if a string has more than 2 consecutive spaces,
    then replace all consecutive spaces with -
    """
    import re
    text = re.sub(r' {3,}', '-', text)
    text = re.sub(r' ', '_', text)
    return text

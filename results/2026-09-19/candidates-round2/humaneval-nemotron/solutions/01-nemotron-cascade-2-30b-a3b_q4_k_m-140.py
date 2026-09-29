def fix_spaces(text):
    """
    Given a string text, replace all spaces in it with underscores, 
    and if a string has more than 2 consecutive spaces, 
    then replace all consecutive spaces with - 
    
    fix_spaces("Example") == "Example"
    fix_spaces("Example 1") == "Example_1"
    fix_spaces(" Example 2") == "_Example_2"
    fix_spaces(" Example   3") == "_Example-3"
    """
    # Replace single or double spaces with underscores
    import re
    text = re.sub(r' {1,2}', '_', text)
    # Replace three or more consecutive spaces with hyphens
    text = re.sub(r' {3,}', '-', text)
    return text

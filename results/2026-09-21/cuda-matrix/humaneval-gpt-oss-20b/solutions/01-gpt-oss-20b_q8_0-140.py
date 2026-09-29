def fix_spaces(text: str) -> str:
    """
    Given a string text, replace all spaces in it with underscores, 
    and if a string has more than 2 consecutive spaces, 
    then replace all consecutive spaces with '-'.

    Examples:
        fix_spaces("Example") == "Example"
        fix_spaces("Example 1") == "Example_1"
        fix_spaces(" Example 2") == "_Example_2"
        fix_spaces(" Example   3") == "_Example-3"
    """
    result = []
    i = 0
    n = len(text)

    while i < n:
        if text[i] == ' ':
            # Count consecutive spaces
            j = i
            while j < n and text[j] == ' ':
                j += 1
            count = j - i
            if count > 2:
                result.append('-')
            else:
                result.extend('_' * count)
            i = j
        else:
            result.append(text[i])
            i += 1

    return ''.join(result)

def file_name_check(file_name: str) -> str:
    """
    Return 'Yes' if file_name is valid according to the rules, otherwise 'No'.
    """
    # Must contain exactly one dot
    if file_name.count('.') != 1:
        return 'No'

    name, ext = file_name.split('.')
    # Extension must be one of the allowed ones
    if ext not in {'txt', 'exe', 'dll'}:
        return 'No'

    # Name part must not be empty and must start with a latin letter
    if not name or not name[0].isalpha() or not name[0].isascii():
        return 'No'

    # Count digits in the entire file name (including extension)
    digit_count = sum(c.isdigit() for c in file_name)
    if digit_count > 3:
        return 'No'

    return 'Yes'

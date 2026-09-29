def check_dict_case(d):
    """
    Given a dictionary, return True if all keys are strings in lower case
    or all keys are strings in upper case, else return False.
    The function should return False if the given dictionary is empty.
    """
    if not d:
        return False

    # Find the first string key to determine the expected case
    expected_case = None
    for key in d:
        if not isinstance(key, str):
            return False
        if expected_case is None:
            if key.islower():
                expected_case = "lower"
            elif key.isupper():
                expected_case = "upper"
            else:
                # Mixed case key (e.g., "Name") is not allowed
                return False

    # Verify all keys match the expected case
    for key in d:
        if expected_case == "lower" and not key.islower():
            return False
        if expected_case == "upper" and not key.isupper():
            return False

    return True

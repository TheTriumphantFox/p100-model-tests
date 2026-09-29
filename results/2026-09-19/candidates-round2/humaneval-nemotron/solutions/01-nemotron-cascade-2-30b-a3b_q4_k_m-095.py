def check_dict_case(d):
    """
    Given a dictionary, return True if all keys are strings in lower case 
    or all keys are strings in upper case, else return False.
    The function should return False if the given dictionary is empty.
    """
    if not d:
        return False

    # Ensure all keys are strings
    for k in d:
        if not isinstance(k, str):
            return False

    # Determine if all keys are lower case or all are upper case
    all_lower = all(k.islower() for k in d)
    all_upper = all(k.isupper() for k in d)

    return all_lower or all_upper

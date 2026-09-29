def check_dict_case(dict):
    """
    Given a dictionary, return True if all keys are strings in lower
    case or all keys are strings in upper case, else return False.
    The function should return False is the given dictionary is empty.
    Examples:
    check_dict_case({"a":"apple", "b":"banana"}) should return True.
    check_dict_case({"a":"apple", "A":"banana", "B":"banana"}) should return False.
    check_dict_case({"a":"apple", 8:"banana", "a":"apple"}) should return False.
    check_dict_case({"Name":"John", "Age":"36", "City":"Houston"}) should return False.
    check_dict_case({"STATE":"NC", "ZIP":"12345" }) should return True.
    """
    if not dict:
        return False

    keys = dict.keys()
    all_lower = all(isinstance(k, str) and k.islower() for k in keys)
    all_upper = all(isinstance(k, str) and k.isupper() for k in keys)

    return all_lower or all_upper

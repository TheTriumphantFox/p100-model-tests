def compare_one(a, b):
    """
    Create a function that takes integers, floats, or strings representing
    real numbers, and returns the larger variable in its given variable type.
    Return None if the values are equal.
    Note: If a real number is represented as a string, the floating point might be . or ,

    compare_one(1, 2.5) ➞ 2.5
    compare_one(1, "2,3") ➞ "2,3"
    compare_one("5,1", "6") ➞ "6"
    compare_one("1", 1) ➞ None
    """
    def to_float(val):
        if isinstance(val, str):
            # Replace comma with dot for floating point
            return float(val.replace(',', '.'))
        else:
            return float(val)
    
    a_val = to_float(a)
    b_val = to_float(b)
    
    if a_val > b_val:
        return a
    elif b_val > a_val:
        return b
    else:
        return None

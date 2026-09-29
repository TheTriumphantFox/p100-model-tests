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
    def parse_number(x):
        if isinstance(x, (int, float)):
            return x
        if isinstance(x, str):
            try:
                return float(x.replace(',', '.'))
            except ValueError:
                return None
        return None

    def get_type(x):
        if isinstance(x, str):
            return str
        if isinstance(x, float):
            return float
        if isinstance(x, int):
            return int
        return None

    a_parsed = parse_number(a)
    b_parsed = parse_number(b)

    if a_parsed is None or b_parsed is None:
        if isinstance(a, str) and isinstance(b, str):
            return a if a > b else b if b > a else None
        return None

    if a_parsed == b_parsed:
        return None

    if a_parsed > b_parsed:
        return a if get_type(a) == get_type(a_parsed) else a_parsed
    else:
        return b if get_type(b) == get_type(b_parsed) else b_parsed

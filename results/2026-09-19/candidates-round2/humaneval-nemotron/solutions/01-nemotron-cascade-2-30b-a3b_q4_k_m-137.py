def compare_one(a, b):
    """
    Create a function that takes integers, floats, or strings representing
    real numbers, and returns the larger variable in its given variable type.
    Return None if the values are equal.

    The function accepts:
        - int, float: passed directly.
        - str: may contain a decimal separator either '.' or ','.
               The string is converted to a float for comparison,
               but the original string (with its original separator) is
               returned as the larger value.

    If both arguments represent the same numeric value, the function returns None.
    """
    # Helper to convert a value to a comparable float.
    def to_float(x):
        if isinstance(x, (int, float)):
            return float(x)
        if isinstance(x, str):
            # Replace possible thousands separator ',' with '.' for conversion.
            # The problem statement only mentions that the decimal separator may be ','.
            # We'll replace ',' with '.' to allow conversion.
            return float(x.replace(',', '.'))
        raise TypeError("Unsupported type for comparison")

    # Compute numeric values.
    try:
        a_val = to_float(a)
        b_val = to_float(b)
    except (ValueError, TypeError):
        # If conversion fails, we cannot compare; return None.
        return None

    # Compare numeric values.
    if a_val > b_val:
        return a
    if b_val > a_val:
        return b
    # Values are equal.
    return None

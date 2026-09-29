def decimal_to_binary(decimal):
    """Convert a decimal integer to a binary string with 'db' markers.

    Parameters
    ----------
    decimal : int
        The decimal number to convert.

    Returns
    -------
    str
        A string in the form 'db<binary>db', where <binary> is the binary
        representation of the input number without any leading zeros.
    """
    if not isinstance(decimal, int):
        raise TypeError("Input must be an integer")
    if decimal < 0:
        raise ValueError("Input must be non-negative")

    binary_part = bin(decimal)[2:]  # strip the '0b' prefix
    return f"db{binary_part}db"

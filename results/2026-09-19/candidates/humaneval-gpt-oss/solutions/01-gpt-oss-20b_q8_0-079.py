def decimal_to_binary(decimal: int) -> str:
    """
    Convert a decimal integer to a binary string with a 'db' prefix and suffix.

    Parameters
    ----------
    decimal : int
        The decimal number to convert.

    Returns
    -------
    str
        The binary representation of the number surrounded by 'db'.
        For example, decimal_to_binary(15) returns "db1111db".
    """
    # Convert to binary without the '0b' prefix
    binary_part = bin(decimal)[2:]
    # Add the required 'db' markers
    return f"db{binary_part}db"

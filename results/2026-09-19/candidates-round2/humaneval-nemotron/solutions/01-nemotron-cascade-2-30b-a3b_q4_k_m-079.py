def decimal_to_binary(decimal):
    """Convert a decimal integer to a binary string with 'db' prefix and suffix.

    The binary representation does not include the '0b' prefix and is padded
    with 'db' at the beginning and end as required.

    Args:
        decimal (int): A non‑negative integer to convert.

    Returns:
        str: The binary representation surrounded by 'db' on both sides.
    """
    if not isinstance(decimal, int) or decimal < 0:
        raise ValueError("Input must be a non‑negative integer")

    # Convert to binary without the '0b' prefix
    binary_str = bin(decimal)[2:]

    # Add the required 'db' markers
    return f"db{binary_str}db"

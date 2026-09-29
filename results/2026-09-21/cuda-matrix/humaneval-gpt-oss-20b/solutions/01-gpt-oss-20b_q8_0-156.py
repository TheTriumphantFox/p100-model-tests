def int_to_mini_roman(number: int) -> str:
    """
    Convert a positive integer (1 <= number <= 1000) to its Roman numeral
    representation in lowercase.

    Parameters
    ----------
    number : int
        The integer to convert.

    Returns
    -------
    str
        The Roman numeral representation in lowercase.

    Examples
    --------
    >>> int_to_mini_roman(19)
    'xix'
    >>> int_to_mini_roman(152)
    'clii'
    >>> int_to_mini_roman(426)
    'cdxxvi'
    """
    if not (1 <= number <= 1000):
        raise ValueError("Number must be between 1 and 1000 inclusive")

    # Mapping of integer values to Roman numeral symbols
    roman_map = [
        (1000, "M"),
        (900,  "CM"),
        (500,  "D"),
        (400,  "CD"),
        (100,  "C"),
        (90,   "XC"),
        (50,   "L"),
        (40,   "XL"),
        (10,   "X"),
        (9,    "IX"),
        (5,    "V"),
        (4,    "IV"),
        (1,    "I"),
    ]

    result = []
    remaining = number
    for value, symbol in roman_map:
        while remaining >= value:
            result.append(symbol)
            remaining -= value

    return "".join(result).lower()

def int_to_mini_roman(number):
    """
    Given a positive integer, obtain its roman numeral equivalent as a string,
    and return it in lowercase.
    Restrictions: 1 <= num <= 1000

    Examples:
    >>> int_to_mini_roman(19) == 'xix'
    >>> int_to_mini_roman(152) == 'clii'
    >>> int_to_mini_roman(426) == 'cdxxvi'
    """
    val = [
        1000, 900, 500, 400,
        100, 90, 50, 40,
        10, 9, 5, 4,
        1
    ]
    syms = [
        'm', 'cm', 'd', 'cd',
        'c', 'xc', 'l', 'xl',
        'x', 'ix', 'v', 'iv',
        'i'
    ]
    integer = number
    res = []
    for i in range(len(val)):
        while integer >= val[i]:
            res.append(syms[i])
            integer -= val[i]
    return ''.join(res)

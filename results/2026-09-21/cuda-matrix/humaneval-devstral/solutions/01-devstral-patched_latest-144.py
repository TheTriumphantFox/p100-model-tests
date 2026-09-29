def simplify(x, n):
    """Your task is to implement a function that will simplify the expression
    x * n. The function returns True if x * n evaluates to a whole number and False
    otherwise. Both x and n, are string representation of a fraction, and have the following format,
    <numerator>/<denominator> where both numerator and denominator are positive whole numbers.

    You can assume that x, and n are valid fractions, and do not have zero as denominator.

    simplify("1/5", "5/1") = True
    simplify("1/6", "2/1") = False
    simplify("7/10", "10/2") = False
    """
    def parse_fraction(s):
        num, denom = map(int, s.split('/'))
        return num, denom

    x_num, x_denom = parse_fraction(x)
    n_num, n_denom = parse_fraction(n)

    # The product x * n is (x_num * n_num) / (x_denom * n_denom)
    # We need to check if (x_num * n_num) is divisible by (x_denom * n_denom)
    numerator = x_num * n_num
    denominator = x_denom * n_denom

    return numerator % denominator == 0

def digits(n):
    """Given a positive integer n, return the product of the odd digits.
    Return 0 if all digits are even.
    For example:
    digits(1)  == 1
    digits(4)  == 0
    digits(235) == 15
    """
    product = 1
    has_odd = False
    for digit in str(n):
        d = int(digit)
        if d % 2 == 1:
            has_odd = True
            product *= d
    return product if has_odd else 0

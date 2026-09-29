def digits(n: int) -> int:
    """Given a positive integer n, return the product of the odd digits.
    Return 0 if all digits are even.
    For example:
    digits(1)  == 1
    digits(4)  == 0
    digits(235) == 15
    """
    product = 1
    has_odd = False
    while n > 0:
        d = n % 10
        if d % 2 == 1:          # odd digit
            product *= d
            has_odd = True
        n //= 10
    return product if has_odd else 0

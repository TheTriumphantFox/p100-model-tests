import math

def is_simple_power(x, n):
    """Your task is to write a function that returns true if a number x is a simple
    power of n and false in other cases.
    x is a simple power of n if n**int=x
    For example:
    is_simple_power(1, 4) => true
    is_simple_power(2, 2) => true
    is_simple_power(8, 2) => true
    is_simple_power(3, 2) => false
    is_simple_power(3, 1) => false
    is_simple_power(5, 3) => false
    """
    if n == 1:
        return False
    if x == 1:
        return True
    if n == 0:
        return False
    
    # Calculate the logarithm base n of x
    # If x is a power of n, log_n(x) should be an integer
    log_val = math.log(x, n)
    
    # Check if the result is an integer
    return abs(log_val - round(log_val)) < 1e-10

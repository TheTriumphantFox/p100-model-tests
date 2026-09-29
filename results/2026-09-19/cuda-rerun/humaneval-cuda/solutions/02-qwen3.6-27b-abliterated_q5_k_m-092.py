def any_int(x, y, z):
    '''
    Create a function that takes 3 numbers.
    Returns true if one of the numbers is equal to the sum of the other two, and all numbers are integers.
    Returns false in any other cases.
    
    Examples
    any_int(5, 2, 7) ➞ True
    
    any_int(3, 2, 2) ➞ False

    any_int(3, -2, 1) ➞ True
    
    any_int(3.6, -2.2, 2) ➞ False
  
    
    '''
    # Check if all numbers are integers
    if not (isinstance(x, int) and isinstance(y, int) and isinstance(z, int)):
        # Also handle booleans since bool is a subclass of int in Python
        # But typically we want strict int check. Let's check more carefully.
        # Actually, isinstance(True, int) is True, but True is not typically considered an "integer" in this context.
        # Let's check if they are ints but not bools.
        if isinstance(x, bool) or isinstance(y, bool) or isinstance(z, bool):
            return False
        # If any is not an int (and not a bool), return False
        if not (isinstance(x, int) and isinstance(y, int) and isinstance(z, int)):
            return False
    
    # Check if one number is the sum of the other two
    if x == y + z or y == x + z or z == x + y:
        return True
    
    return False

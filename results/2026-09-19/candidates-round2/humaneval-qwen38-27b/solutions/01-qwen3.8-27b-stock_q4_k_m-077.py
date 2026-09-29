def iscube(a):
    '''
    Write a function that takes an integer a and returns True 
    if this ingeger is a cube of some integer number.
    Note: you may assume the input is always valid.
    Examples:
    iscube(1) ==> True
    iscube(2) ==> False
    iscube(-1) ==> True
    iscube(64) ==> True
    iscube(0) ==> True
    iscube(180) ==> False
    '''
    if a < 0:
        a = -a
    # Find the integer cube root
    # Use round to get the nearest integer
    if a == 0:
        return True
    # Compute cube root
    cube_root = round(a ** (1 / 3))
    # Check nearby values due to floating point precision
    for candidate in (cube_root - 1, cube_root, cube_root + 1):
        if candidate >= 0 and candidate ** 3 == a:
            return True
    return False

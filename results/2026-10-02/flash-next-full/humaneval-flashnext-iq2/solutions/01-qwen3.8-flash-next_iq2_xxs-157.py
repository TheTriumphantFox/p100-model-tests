def right_angle_triangle(a, b, c):
    '''
    Given the lengths of the three sides of a triangle. Return True if the three
    sides form a right-angled triangle, False otherwise.
    A right-angled triangle is a triangle in which one angle is right angle or 
    90 degree.
    Example:
    right_angle_triangle(3, 4, 5) == True
    right_angle_triangle(1, 2, 3) == False
    '''
    sides = sorted([a, b, c])
    a, b, c = sides
    # Check if the Pythagorean theorem holds: a^2 + b^2 == c^2
    # Use a small epsilon for floating point comparison if needed, but for integer inputs exact match is fine.
    # However, to be robust, we check with a small tolerance.
    epsilon = 1e-9
    return abs(a**2 + b**2 - c**2) < epsilon

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
    # Check if all sides are positive
    if a <= 0 or b <= 0 or c <= 0:
        return False
    
    # Sort the sides so that the largest is last
    sides = sorted([a, b, c])
    
    # Check Pythagorean theorem: a^2 + b^2 = c^2
    return sides[0] ** 2 + sides[1] ** 2 == sides[2] ** 2

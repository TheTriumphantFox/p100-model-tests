def choose_num(x, y):
    """This function takes two positive numbers x and y and returns the
    biggest even integer number that is in the range [x, y] inclusive. If 
    there's no such number, then the function should return -1.

    For example:
    choose_num(12, 15) = 14
    choose_num(13, 12) = -1
    """
    if x > y:
        return -1
    
    # Find the largest number in the range
    max_num = y
    
    # If the largest number is odd, decrement it to find the largest even number
    if max_num % 2 != 0:
        max_num -= 1
        
    return max_num

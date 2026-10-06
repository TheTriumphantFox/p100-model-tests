def prod_signs(arr):
    """
    You are given an array arr of integers and you need to return
    sum of magnitudes of integers multiplied by product of all signs
    of each number in the array, represented by 1, -1 or 0.
    Note: return None for empty arr.

    Example:
    >>> prod_signs([1, 2, 2, -4]) == -9
    >>> prod_signs([0, 1]) == 0
    >>> prod_signs([]) == None
    """
    if not arr:
        return None
    
    # Calculate the product of signs
    sign_product = 1
    for num in arr:
        if num > 0:
            sign_product *= 1
        elif num < 0:
            sign_product *= -1
        else:
            sign_product = 0
            break
    
    # Calculate the sum of magnitudes
    magnitude_sum = sum(abs(num) for num in arr)
    
    # Multiply the sum of magnitudes by the product of signs
    result = magnitude_sum * sign_product
    
    return result

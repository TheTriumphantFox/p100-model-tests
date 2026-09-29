def largest_smallest_integers(lst):
    '''
    Create a function that returns a tuple (a, b), where 'a' is
    the largest of negative integers, and 'b' is the smallest
    of positive integers in a list.
    If there is no negative or positive integers, return them as None.

    Examples:
    largest_smallest_integers([2, 4, 1, 3, 5, 7]) == (None, 1)
    largest_smallest_integers([]) == (None, None)
    largest_smallest_integers([0]) == (None, None)
    '''
    largest_neg = None
    smallest_pos = None
    
    for num in lst:
        if num < 0:
            if largest_neg is None or num > largest_neg:
                largest_neg = num
        elif num > 0:
            if smallest_pos is None or num < smallest_pos:
                smallest_pos = num
                
    return (largest_neg, smallest_pos)

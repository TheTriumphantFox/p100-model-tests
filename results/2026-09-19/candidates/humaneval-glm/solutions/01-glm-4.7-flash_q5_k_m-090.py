def next_smallest(lst):
    """
    You are given a list of integers.
    Write a function next_smallest() that returns the 2nd smallest element of the list.
    Return None if there is no such element.
    
    next_smallest([1, 2, 3, 4, 5]) == 2
    next_smallest([5, 1, 4, 3, 2]) == 2
    next_smallest([]) == None
    next_smallest([1, 1]) == None
    """
    # Create a set to remove duplicates
    unique_numbers = set(lst)
    
    # Check if there are at least 2 unique numbers
    if len(unique_numbers) < 2:
        return None
    
    # Sort the unique numbers and return the second one
    return sorted(unique_numbers)[1]

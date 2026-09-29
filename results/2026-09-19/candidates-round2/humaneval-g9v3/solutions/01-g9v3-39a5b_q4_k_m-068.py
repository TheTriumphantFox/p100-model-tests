def pluck(arr):
    """
    Given an array representing a branch of a tree that has non-negative integer nodes
    your task is to pluck one of the nodes and return it.
    The plucked node should be the node with the smallest even value.
    If multiple nodes with the same smallest even value are found return the node that has smallest index.

    The plucked node should be returned in a list, [ smalest_value, its index ],
    If there are no even values or the given array is empty, return [].
    """
    if not arr:
        return []
    
    min_even = None
    min_index = None
    
    for i, val in enumerate(arr):
        if val % 2 == 0:
            if min_even is None or val < min_even:
                min_even = val
                min_index = i
                
    if min_even is None:
        return []
        
    return [min_even, min_index]

def next_smallest(lst):
    """
    Return the second smallest distinct element in the list.
    If it does not exist, return None.
    """
    # Use a set to keep distinct values
    distinct = set(lst)
    if len(distinct) < 2:
        return None
    # Find the smallest and second smallest
    smallest = min(distinct)
    # Remove the smallest and get the new minimum
    distinct.remove(smallest)
    return min(distinct)

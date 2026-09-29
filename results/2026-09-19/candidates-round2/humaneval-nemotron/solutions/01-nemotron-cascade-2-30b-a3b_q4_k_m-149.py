def sorted_list_sum(lst):
    """
    Accepts a list of strings, removes strings with odd lengths,
    and returns the remaining strings sorted by ascending length.
    For strings of equal length, they are sorted alphabetically.

    Parameters:
        lst (list of str): The input list of strings.

    Returns:
        list of str: The filtered and sorted list of strings.
    """
    # Filter out strings with odd lengths
    filtered = [s for s in lst if len(s) % 2 == 0]
    # Sort by length first, then alphabetically for equal lengths
    filtered.sort(key=lambda x: (len(x), x))
    return filtered

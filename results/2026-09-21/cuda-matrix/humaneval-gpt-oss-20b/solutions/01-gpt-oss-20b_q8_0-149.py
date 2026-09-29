def sorted_list_sum(lst):
    """
    Accepts a list of strings, removes strings with odd lengths,
    and returns the remaining strings sorted first by length (ascending)
    and then alphabetically for strings of equal length.
    """
    # Keep only strings with even length
    even_strings = [s for s in lst if len(s) % 2 == 0]

    # Sort by length, then alphabetically
    even_strings.sort(key=lambda s: (len(s), s))
    return even_strings

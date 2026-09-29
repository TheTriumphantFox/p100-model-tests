def next_smallest(lst):
    if len(lst) < 2:
        return None
    unique = list(set(lst))
    if len(unique) < 2:
        return None
    unique.sort()
    return unique[1]

def largest_smallest_integers(lst):
    negatives = [x for x in lst if isinstance(x, int) and x < 0]
    positives = [x for x in lst if isinstance(x, int) and x > 0]
    a = max(negatives) if negatives else None
    b = min(positives) if positives else None
    return (a, b)

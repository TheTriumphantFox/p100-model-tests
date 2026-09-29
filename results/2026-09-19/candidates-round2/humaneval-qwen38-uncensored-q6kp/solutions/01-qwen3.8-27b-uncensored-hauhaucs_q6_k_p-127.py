def intersection(interval1, interval2):
    """You are given two intervals,
    where each interval is a pair of integers. For example, interval = (start, end) = (1, 2).
    The given intervals are closed which means that the interval (start, end)
    includes both start and end.
    For each given interval, it is assumed that its start is less or equal its end.
    Your task is to determine whether the length of intersection of these two 
    intervals is a prime number.
    Example, the intersection of the intervals (1, 3), (2, 4) is (2, 3)
    which its length is 1, which not a prime number.
    If the length of the intersection is a prime number, return "YES",
    otherwise, return "NO".
    If the two intervals don't intersect, return "NO".


    [input/output] samples:
    intersection((1, 2), (2, 3)) ==> "NO"
    intersection((-1, 1), (0, 4)) ==> "NO"
    intersection((-3, -1), (-5, 5)) ==> "YES"
    """
    start1, end1 = interval1
    start2, end2 = interval2
    
    # Find the intersection
    inter_start = max(start1, start2)
    inter_end = min(end1, end2)
    
    # Check if there is an intersection
    if inter_start > inter_end:
        return "NO"
    
    # The length of the intersection (number of integer points)
    length = inter_end - inter_start + 1
    
    # Check if length is a prime number
    if length < 2:
        return "NO"
    
    if length == 2:
        return "YES"
    
    if length % 2 == 0:
        return "NO"
    
    for i in range(3, int(length**0.5) + 1, 2):
        if length % i == 0:
            return "NO"
    
    return "YES"

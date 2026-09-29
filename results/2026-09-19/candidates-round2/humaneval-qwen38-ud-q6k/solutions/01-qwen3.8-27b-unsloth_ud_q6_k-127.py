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
    # For closed intervals [a, b], the length in terms of count is b - a + 1
    # But the problem says "length of intersection" - let's check the examples.
    # Example: (1, 3) and (2, 4) intersect at (2, 3), length is 1.
    # If we use b - a + 1: 3 - 2 + 1 = 2, which is prime. But expected is "NO".
    # If we use b - a: 3 - 2 = 1, which is not prime. Expected "NO". So length = inter_end - inter_start.
    
    length = inter_end - inter_start
    
    # Check if length is prime
    if length < 2:
        return "NO"
    
    # Check for primality
    if length == 2:
        return "YES"
    if length % 2 == 0:
        return "NO"
    
    i = 3
    while i * i <= length:
        if length % i == 0:
            return "NO"
        i += 2
    
    return "YES"

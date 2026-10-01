def get_max_triples(n):
    """
    You are given a positive integer n. You have to create an integer array a of length n.
        For each i (1 ≤ i ≤ n), the value of a[i] = i * i - i + 1.
        Return the number of triples (a[i], a[j], a[k]) of a where i < j < k, 
    and a[i] + a[j] + a[k] is a multiple of 3.

    Example :
        Input: n = 5
        Output: 1
        Explanation: 
        a = [1, 3, 7, 13, 21]
        The only valid triple is (1, 7, 13).
    """
    if n < 3:
        return 0
    
    # Compute the array a
    a = [i * i - i + 1 for i in range(1, n + 1)]
    
    # Count how many elements have remainder 0, 1, 2 when divided by 3
    count = [0, 0, 0]
    for val in a:
        count[val % 3] += 1
    
    # The sum of three numbers is divisible by 3 if:
    # 1. All three have remainder 0: count[0] choose 3
    # 2. All three have remainder 1: count[1] choose 3
    # 3. All three have remainder 2: count[2] choose 3
    # 4. One of each remainder: count[0] * count[1] * count[2]
    
    def choose3(x):
        if x < 3:
            return 0
        return x * (x - 1) * (x - 2) // 6
    
    result = choose3(count[0]) + choose3(count[1]) + choose3(count[2]) + count[0] * count[1] * count[2]
    
    return result

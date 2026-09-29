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
    count0 = 0  # indices where i%3 == 2, a[i] % 3 == 0
    count1 = 0  # indices where i%3 == 0 or 1, a[i] % 3 == 1
    
    for i in range(1, n + 1):
        if i % 3 == 2:
            count0 += 1
        else:
            count1 += 1
    
    # We need either three 0s or three 1s
    triples_from_0 = count0 * (count0 - 1) * (count0 - 2) // 6 if count0 >= 3 else 0
    triples_from_1 = count1 * (count1 - 1) * (count1 - 2) // 6 if count1 >= 3 else 0
    
    return triples_from_0 + triples_from_1

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
    counts = [0, 0, 0]
    for i in range(1, n + 1):
        counts[(i * i - i + 1) % 3] += 1

    c0, c1, c2 = counts
    return c0 * (c0 - 1) * (c0 - 2) // 6 + \
           c1 * (c1 - 1) * (c1 - 2) // 6 + \
           c2 * (c2 - 1) * (c2 - 2) // 6 + \
           c0 * c1 * c2

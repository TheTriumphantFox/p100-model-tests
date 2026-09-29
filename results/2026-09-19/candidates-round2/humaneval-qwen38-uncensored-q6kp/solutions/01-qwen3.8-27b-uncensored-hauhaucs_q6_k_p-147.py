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
    # We need to count triples (i, j, k) with i < j < k such that
    # (a[i] + a[j] + a[k]) % 3 == 0
    # where a[i] = i*i - i + 1
    
    # Let's analyze a[i] mod 3:
    # a[i] = i^2 - i + 1
    # For i mod 3:
    #   i = 0: 0 - 0 + 1 = 1 mod 3
    #   i = 1: 1 - 1 + 1 = 1 mod 3
    #   i = 2: 4 - 2 + 1 = 3 = 0 mod 3
    # So a[i] mod 3 depends on i mod 3:
    #   i mod 3 == 0 -> a[i] mod 3 == 1
    #   i mod 3 == 1 -> a[i] mod 3 == 1
    #   i mod 3 == 2 -> a[i] mod 3 == 0
    
    # Let's count how many indices i (1-indexed) have each residue mod 3.
    # i ranges from 1 to n.
    # i mod 3 == 0: i = 3, 6, 9, ... -> count = n // 3
    # i mod 3 == 1: i = 1, 4, 7, ... -> count = (n + 2) // 3
    # i mod 3 == 2: i = 2, 5, 8, ... -> count = (n + 1) // 3
    
    # Let:
    # c0 = number of i with i mod 3 == 0 -> a[i] mod 3 == 1
    # c1 = number of i with i mod 3 == 1 -> a[i] mod 3 == 1
    # c2 = number of i with i mod 3 == 2 -> a[i] mod 3 == 0
    
    # So we have:
    # count of a[i] mod 3 == 0: c2
    # count of a[i] mod 3 == 1: c0 + c1
    # count of a[i] mod 3 == 2: 0
    
    # Wait, let me recheck. a[i] mod 3 can only be 0 or 1? Let me verify:
    # i=1: 1-1+1=1, 1 mod 3 = 1
    # i=2: 4-2+1=3, 3 mod 3 = 0
    # i=3: 9-3+1=7, 7 mod 3 = 1
    # i=4: 16-4+1=13, 13 mod 3 = 1
    # i=5: 25-5+1=21, 21 mod 3 = 0
    # i=6: 36-6+1=31, 31 mod 3 = 1
    # i=7: 49-7+1=43, 43 mod 3 = 1
    # i=8: 64-8+1=57, 57 mod 3 = 0
    # So indeed, a[i] mod 3 is either 0 or 1.
    
    # For a[i] + a[j] + a[k] to be 0 mod 3, we need the sum of three values each in {0, 1} to be 0 mod 3.
    # Possible sums: 0, 1, 2, 3
    #

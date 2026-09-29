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
    # Compute a[i] mod 3 for i from 1 to n
    # a[i] = i*i - i + 1
    # Let's find the pattern of a[i] mod 3
    # i mod 3: 0, 1, 2
    # i=1: 1-1+1=1 -> 1 mod 3
    # i=2: 4-2+1=3 -> 0 mod 3
    # i=3: 9-3+1=7 -> 1 mod 3
    # i=4: 16-4+1=13 -> 1 mod 3
    # i=5: 25-5+1=21 -> 0 mod 3
    # i=6: 36-6+1=31 -> 1 mod 3
    # i=7: 49-7+1=43 -> 1 mod 3
    # i=8: 64-8+1=57 -> 0 mod 3
    # i=9: 81-9+1=73 -> 1 mod 3
    # i=10: 100-10+1=91 -> 1 mod 3
    # i=11: 121-11+1=111 -> 0 mod 3
    # i=12: 144-12+1=133 -> 1 mod 3
    
    # Let's compute more carefully:
    # i mod 3 = 0: i=3,6,9,12
    #   i=3: 9-3+1=7, 7%3=1
    #   i=6: 36-6+1=31, 31%3=1
    #   i=9: 81-9+1=73, 73%3=1
    #   i=12: 144-12+1=133, 133%3=1
    # i mod 3 = 1: i=1,4,7,10
    #   i=1: 1-1+1=1, 1%3=1
    #   i=4: 16-4+1=13, 13%3=1
    #   i=7: 49-7+1=43, 43%3=1
    #   i=10: 100-10+1=91, 91%3=1
    # i mod 3 = 2: i=2,5,8,11
    #   i=2: 4-2+1=3, 3%3=0
    #   i=5: 25-5+1=21, 21%3=0
    #   i=8: 64-8+1=57, 57%3=0
    #   i=11: 121-11+1=111, 111%3=0
    
    # So:
    # if i % 3 == 0: a[i] % 3 = 1
    # if i % 3 == 1: a[i] % 3 = 1
    # if i % 3 == 2: a[i] % 3 = 0
    
    # Wait, let me double-check with the example:
    # n=5, a = [1, 3, 7, 13, 21]
    # a[1]=1 (i=1,

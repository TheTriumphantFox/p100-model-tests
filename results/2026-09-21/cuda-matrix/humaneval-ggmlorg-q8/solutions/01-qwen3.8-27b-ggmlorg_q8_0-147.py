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
    # Compute a[i] for i from 1 to n
    # a[i] = i*i - i + 1
    # We need to count triples (i, j, k) with i < j < k such that a[i] + a[j] + a[k] ≡ 0 (mod 3)
    
    # Let's compute the residues of a[i] mod 3 for i = 1 to n
    # a[i] = i^2 - i + 1
    # Let's find the pattern of a[i] mod 3:
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
    
    # Pattern: for i mod 3:
    # i ≡ 1 (mod 3): a[i] ≡ 1 (mod 3)
    # i ≡ 2 (mod 3): a[i] ≡ 0 (mod 3)
    # i ≡ 0 (mod 3): a[i] ≡ 1 (mod 3)
    
    # So residues:
    # i mod 3 = 0 -> residue 1
    # i mod 3 = 1 -> residue 1
    # i mod 3 = 2 -> residue 0
    
    # Let's verify:
    # i=1: 1 mod 3 = 1 -> residue 1 ✓
    # i=2: 2 mod 3 = 2 -> residue 0 ✓
    # i=3: 3 mod 3 = 0 -> residue 1 ✓
    # i=4: 4 mod 3 = 1 -> residue 1 ✓
    # i=5: 5 mod 3 = 2 -> residue 0 ✓
    # i=6: 6 mod 3 = 0 -> residue 1 ✓
    
    # So we have:
    # count_0 = number of i in [1, n] with i mod 3 == 2
    # count_1 = number of i in [1, n] with i mod 3 == 0 or i mod 3 == 1
    # count_2 = 0 (no residues of 2)
    
    # Wait, let me re-check. The residues are only 0 and 1.
    # For a triple to sum to 0 mod 3, we need:
    # - All three residues are 0: 0+0+0=0
    # - Two residues are 1 and one is 1: 1+1+1=3≡0
    # - One residue is 0 and two are... wait, 0+1

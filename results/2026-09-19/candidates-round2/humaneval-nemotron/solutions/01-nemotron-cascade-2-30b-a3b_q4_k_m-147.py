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
    # Compute residues of a[i] modulo 3 for i = 1..n
    # a[i] = i^2 - i + 1
    # i^2 - i = i*(i-1) is always even, but we only need modulo 3.
    # Compute i mod 3 and (i-1) mod 3 to get (i^2 - i) mod 3, then add 1.
    # Simplify: (i^2 - i + 1) mod 3 = (i*(i-1) + 1) mod 3
    # We can precompute for i mod 3 = 0,1,2:
    #   i mod 3 = 0 -> i*(i-1) mod 3 = 0*2 = 0 -> +1 => 1
    #   i mod 3 = 1 -> 1*0 = 0 -> +1 => 1
    #   i mod 3 = 2 -> 2*1 = 2 -> +1 => 0
    # So residues are 1 for i ≡ 0 or 1 (mod 3), and 0 for i ≡ 2 (mod 3).
    count0 = n // 3                     # i ≡ 2 (mod 3)
    count1 = n - count0                 # i ≡ 0 or 1 (mod 3)

    # Count triples where sum of residues ≡ 0 (mod 3)
    # Possible residue combinations (r1, r2, r3) with r1+r2+r3 ≡ 0:
    #   (0,0,0) -> C(count0, 3)
    #   (1,1,1) -> C(count1, 3)
    #   (0,1,2) but residue 2 doesn't exist, so skip
    #   (0,0,1) -> 2*1+0 = 2 mod 3 -> not 0
    #   (0,1,1) -> 0+1+1 = 2 mod 3 -> not 0
    #   (1,1,0) same as above
    #   (0,0,0) and (1,1,1) are the only valid ones.

    def nCr3(x):
        if x < 3:
            return 0
        return x * (x - 1) * (x - 2) // 6

    total = nCr3(count0) + nCr3(count1)
    return total

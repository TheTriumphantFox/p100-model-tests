def get_max_triples(n: int) -> int:
    """
    Count triples (a[i], a[j], a[k]) with i < j < k such that
    a[i] + a[j] + a[k] is a multiple of 3, where a[i] = i*i - i + 1.
    """
    # Count how many elements of each residue modulo 3
    cnt = [0, 0, 0]
    for i in range(1, n + 1):
        val = i * i - i + 1
        cnt[val % 3] += 1

    c0, c1, c2 = cnt

    # Helper to compute nC3
    def comb3(x: int) -> int:
        return x * (x - 1) * (x - 2) // 6 if x >= 3 else 0

    # Triples with residues (0,0,0), (1,1,1), (2,2,2)
    total = comb3(c0) + comb3(c1) + comb3(c2)

    # Triples with one of each residue (0,1,2)
    total += c0 * c1 * c2

    return total

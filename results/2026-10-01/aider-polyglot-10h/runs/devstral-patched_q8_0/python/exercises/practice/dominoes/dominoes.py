def can_chain(dominoes):
    if not dominoes:
        return []

    # Flatten the dominoes into a list of numbers
    numbers = []
    for d in dominoes:
        numbers.append(d[0])
        numbers.append(d[1])

    # Check if the count of each number is even (except possibly one number which can be odd)
    from collections import Counter
    count = Counter(numbers)
    odd_counts = sum(1 for v in count.values() if v % 2 != 0)

    if odd_counts > 2:
        return None

    # Try to find a valid chain
    from itertools import permutations

    for perm in permutations(dominoes):
        valid = True
        for i in range(len(perm) - 1):
            if perm[i][1] != perm[i+1][0]:
                valid = False
                break
        if valid and perm[0][0] == perm[-1][1]:
            return list(perm)

    return None

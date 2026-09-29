def f(n):
    """Return a list of size n where the element at index i (1‑based) is
    the factorial of i if i is even, otherwise the sum of numbers from 1 to i.
    """
    result = []
    fact = 1  # factorial of 0 (used for even i)
    for i in range(1, n + 1):
        if i % 2 == 0:
            # compute factorial of i
            fact = 1
            for k in range(1, i + 1):
                fact *= k
            result.append(fact)
        else:
            # sum from 1 to i
            result.append(i * (i + 1) // 2)
    return result

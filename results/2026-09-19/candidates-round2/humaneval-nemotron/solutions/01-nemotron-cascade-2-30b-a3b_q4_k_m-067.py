import re

def fruit_distribution(s, n):
    """
    Given a string describing the number of apples and oranges in a basket and the total
    number of fruits in the basket, return the number of mangoes.

    The string always follows the pattern:
        "<A> apples and <O> oranges"
    where <A> and <O> are non‑negative integers (they may have leading zeros).

    Parameters
    ----------
    s : str
        Description of apples and oranges.
    n : int
        Total number of fruits in the basket.

    Returns
    -------
    int
        Number of mangoes (total minus apples minus oranges).

    Examples
    --------
    >>> fruit_distribution("5 apples and 6 oranges", 19)
    8
    >>> fruit_distribution("0 apples and 1 oranges", 3)
    2
    >>> fruit_distribution("2 apples and 3 oranges", 100)
    95
    >>> fruit_distribution("100 apples and 1 oranges", 120)
    19
    """
    # Extract the integer values for apples and oranges using a regular expression.
    # The pattern captures one or more digits for each fruit count.
    match = re.search(r'(\d+)\s+apples?\s+and\s+(\d+)\s+oranges?', s, re.IGNORECASE)
    if not match:
        raise ValueError(f"String does not match the expected format: {s!r}")

    apples = int(match.group(1))
    oranges = int(match.group(2))

    mangoes = n - apples - oranges
    if mangoes < 0:
        # The problem statement does not specify handling of negative results,
        # but returning a negative value would be misleading. We raise an error.
        raise ValueError("Computed mango count is negative; input values are inconsistent.")

    return mangoes

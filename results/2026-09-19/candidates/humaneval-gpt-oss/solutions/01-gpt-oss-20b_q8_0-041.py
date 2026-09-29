def car_race_collision(n: int) -> int:
    """
    Return the number of collisions between two sets of n cars moving in opposite
    directions on an infinitely long straight line.

    All cars move at the same speed and are infinitely sturdy, so each pair of
    cars (one from each set) will collide exactly once.  Therefore the total
    number of collisions is simply n * n.

    Parameters
    ----------
    n : int
        The number of cars in each set.  Must be non‑negative.

    Returns
    -------
    int
        The total number of collisions.
    """
    if n < 0:
        raise ValueError("n must be non‑negative")
    return n * n

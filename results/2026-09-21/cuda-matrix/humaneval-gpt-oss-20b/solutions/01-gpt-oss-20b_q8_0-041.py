def car_race_collision(n: int) -> int:
    """
    Return the total number of collisions between two sets of n cars moving in opposite
    directions on an infinitely long straight road.  All cars have the same speed and
    continue moving after a collision, so each pair of cars (one from each set) will
    collide exactly once.

    Parameters
    ----------
    n : int
        Number of cars in each direction.

    Returns
    -------
    int
        Total number of collisions.
    """
    return n * n

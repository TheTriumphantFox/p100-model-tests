def bf(planet1, planet2):
    """
    Return a tuple of planets whose orbits lie strictly between the orbits of
    planet1 and planet2, sorted by proximity to the Sun.

    Parameters
    ----------
    planet1 : str
        Name of the first planet.
    planet2 : str
        Name of the second planet.

    Returns
    -------
    tuple
        Tuple of planet names between planet1 and planet2. Empty tuple if
        either planet name is invalid.
    """
    # Ordered list of planets from the Sun outward
    planets = [
        "Mercury", "Venus", "Earth", "Mars",
        "Jupiter", "Saturn", "Uranus", "Neptune"
    ]

    # Validate planet names
    if planet1 not in planets or planet2 not in planets:
        return ()

    # Find indices
    idx1 = planets.index(planet1)
    idx2 = planets.index(planet2)

    # Determine the range between the two indices (exclusive)
    if idx1 < idx2:
        between = planets[idx1 + 1:idx2]
    else:
        between = planets[idx2 + 1:idx1]

    return tuple(between)

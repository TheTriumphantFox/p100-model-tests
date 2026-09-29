def bf(planet1: str, planet2: str) -> tuple:
    """
    Return a tuple of planet names that lie strictly between planet1 and planet2
    in the order from the Sun. If either planet name is invalid, return an empty tuple.
    """
    # Ordered list of planets from the Sun
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

    # Determine the range between the two planets (exclusive)
    if idx1 < idx2:
        between = planets[idx1 + 1:idx2]
    else:
        between = planets[idx2 + 1:idx1]

    return tuple(between)

def generate_integers(a, b):
    """
    Given two positive integers a and b, return the even digits between a
    and b, in ascending order.

    For example:
    generate_integers(2, 8) => [2, 4, 6, 8]
    generate_integers(8, 2) => [2, 4, 6, 8]
    generate_integers(10, 14) => []
    """
    # Determine the range
    low = min(a, b)
    high = max(a, b)
    
    # Find all even digits (0-9) that are in the range [low, high]
    even_digits = [d for d in range(10) if d % 2 == 0 and low <= d <= high]
    
    # Sort in ascending order (they are already in ascending order due to range iteration)
    return sorted(even_digits)

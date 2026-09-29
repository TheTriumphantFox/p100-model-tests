def fruit_distribution(s, n):
    """
    Returns the number of mango fruits in the basket.
    
    Parameters:
    s (str): A string representing the number of apples and oranges, e.g., "5 apples and 6 oranges".
    n (int): Total number of fruits in the basket.
    
    Returns:
    int: Number of mango fruits.
    """
    # Split the string into words
    words = s.split()
    
    # Extract the number of apples (first word) and oranges (third word)
    apples = int(words[0])
    oranges = int(words[3])
    
    # Calculate the number of mangoes
    mangoes = n - apples - oranges
    
    return mangoes

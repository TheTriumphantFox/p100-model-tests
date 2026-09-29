import re

def words_string(s):
    """
    Split a string into words separated by commas or spaces.

    Parameters
    ----------
    s : str
        Input string containing words separated by commas or spaces.

    Returns
    -------
    list[str]
        List of words in the order they appear in the input string.
    """
    # Use a regular expression to split on commas or whitespace.
    # The pattern ',|\s+' matches a comma or one or more whitespace characters.
    return [word for word in re.split(r',|\s+', s) if word]

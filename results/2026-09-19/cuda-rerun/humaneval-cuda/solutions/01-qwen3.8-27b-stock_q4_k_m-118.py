def get_closest_vowel(word):
    """You are given a word. Your task is to find the closest vowel that stands between 
    two consonants from the right side of the word (case sensitive).
    
    Vowels in the beginning and ending doesn't count. Return empty string if you didn't
    find any vowel met the above condition. 

    You may assume that the given string contains English letter only.

    Example:
    get_closest_vowel("yogurt") ==> "u"
    get_closest_vowel("FULL") ==> "U"
    get_closest_vowel("quick") ==> ""
    get_closest_vowel("ab") ==> ""
    """
    vowels = set('aeiouAEIOU')
    # We need to find the closest vowel from the right side that is between two consonants
    # Iterate from right to left, but skip the last character (ending doesn't count)
    # and skip the first character (beginning doesn't count)
    # So we consider indices from len(word)-2 down to 1
    for i in range(len(word) - 2, 0, -1):
        if word[i] in vowels:
            # Check if both neighbors are consonants
            left = word[i - 1]
            right = word[i + 1]
            if left not in vowels and right not in vowels:
                return word[i]
    return ""

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
    n = len(word)
    
    # We need to find a vowel that is between two consonants.
    # "From the right side" means we should return the rightmost such vowel.
    # Vowels at the beginning (index 0) or ending (index n-1) don't count.
    
    # Iterate from right to left, starting from index n-2 down to 1
    for i in range(n - 2, 0, -1):
        if word[i] in vowels:
            # Check if the character to the left is a consonant
            left_char = word[i - 1]
            # Check if the character to the right is a consonant
            right_char = word[i + 1]
            
            # A consonant is a letter that is not a vowel
            if left_char not in vowels and right_char not in vowels:
                return word[i]
    
    return ""

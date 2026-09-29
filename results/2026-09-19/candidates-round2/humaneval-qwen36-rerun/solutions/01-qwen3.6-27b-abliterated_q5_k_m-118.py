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
    
    # We need to find a vowel that is between two consonants.
    # "from the right side" means we should search from right to left and return the first match.
    # The vowel must not be at the beginning or end of the word.
    
    # Iterate from right to left, checking each position that could be a vowel between two consonants
    # A vowel at index i is between two consonants if:
    # - i > 0 and i < len(word) - 1 (not at beginning or end)
    # - word[i] is a vowel
    # - word[i-1] is a consonant (not a vowel)
    # - word[i+1] is a consonant (not a vowel)
    
    for i in range(len(word) - 2, 0, -1):
        if word[i] in vowels:
            # Check if both neighbors are consonants
            left_is_consonant = word[i - 1] not in vowels
            right_is_consonant = word[i + 1] not in vowels
            if left_is_consonant and right_is_consonant:
                return word[i]
    
    return ""

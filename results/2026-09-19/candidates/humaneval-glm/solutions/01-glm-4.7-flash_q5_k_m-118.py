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
    vowels = set("aeiouAEIOU")
    length = len(word)
    
    # Iterate from the second to last character (right side)
    for i in range(length - 2, 0, -1):
        current_char = word[i]
        # Check if current char is a vowel
        if current_char in vowels:
            # Check if previous and next chars are consonants
            if word[i - 1] not in vowels and word[i + 1] not in vowels:
                return current_char
                
    return ""

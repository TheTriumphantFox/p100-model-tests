def encode(message):
    """
    Write a function that takes a message, and encodes in such a 
    way that it swaps case of all letters, replaces all vowels in 
    the message with the letter that appears 2 places ahead of that 
    vowel in the english alphabet. 
    Assume only letters. 
    
    Examples:
    >>> encode('test')
    'TGST'
    >>> encode('This is a message')
    'tHKS KS C MGSSCGG'
    """
    vowels = set('aeiouAEIOU')
    result = []
    for char in message:
        if char in vowels:
            # Swap case first, then shift 2 places ahead
            # But we need to be careful: the problem says "replaces all vowels in the message with the letter that appears 2 places ahead of that vowel in the english alphabet"
            # And also "swaps case of all letters"
            # So for a vowel, we first determine the vowel, shift it 2 places ahead, then swap case?
            # Let's check the examples:
            # 'test' -> 'TGST'
            # t -> T (swap case, not a vowel)
            # e -> G (e is a vowel, 2 places ahead is g, then swap case? e is lowercase, 2 ahead is g (lowercase), swap case gives G. Yes.)
            # s -> S (swap case)
            # t -> T (swap case)
            # So: for vowels, shift 2 places ahead in the alphabet (keeping the same case as original), then swap case.
            # Wait, let's re-read: "swaps case of all letters, replaces all vowels in the message with the letter that appears 2 places ahead of that vowel in the english alphabet."
            # This could be interpreted as two operations: 1) swap case of all letters, 2) replace vowels with the letter 2 places ahead.
            # But the order matters. Let's check with 'This is a message':
            # T -> t (swap case)
            # h -> H (swap case)
            # i -> K (i is vowel, 2 ahead is k, swap case? i is lowercase, 2 ahead is k (lowercase), swap case gives K. Yes.)
            # s -> S (swap case)
            # space -> space
            # i -> K (same as above)
            # s -> S
            # space
            # a -> C (a is vowel, 2 ahead is c, swap case gives C)
            # space
            # m -> M
            # e -> G
            # s -> S
            # s -> S
            # a -> C
            # g -> G
            # e -> G
            # So the pattern is: for each character, if it's a vowel, replace it with the letter 2 places ahead (in the same case), then swap the case. If it's not a vowel, just swap the case.
            
            # Determine the base vowel (lowercase for lookup)
            lower_char = char.lower()
            # Shift 2 places ahead
            # For lowercase vowels: a->c, e->g, i->k, o->q, u->w
            # For uppercase vowels: A->C, E->G, I->K, O->Q, U->W
            if lower_char == 'a':
                shifted = 'c' if char.islower() else 'C'
            elif lower_char == 'e':
                shifted = 'g' if char.islower() else 'G'
            elif lower_char == 'i':
                shifted = 'k' if char.islower() else 'K'
            elif lower_char == 'o':
                shifted = 'q' if char.islower() else 'Q'
            elif lower_char == 'u':
                shifted = 'w' if char.islower() else 'W'
            else:
                shifted = char  # shouldn't happen
            
            # Now swap case of the shifted character
            if shifted.islower():
                result.append(shifted.upper())
            else:
                result.append(shifted.lower())
        else:
            # Just swap case
            if char.islower():
                result.append(char.upper())
            else:
                result.append(char.lower())
    
    return ''.join(result)

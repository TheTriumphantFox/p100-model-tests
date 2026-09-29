def encode(message):
    vowels = 'aeiouAEIOU'
    result = []
    for char in message:
        if char.isalpha():
            swapped = char.swapcase()
            if swapped in vowels:
                idx = vowels.index(swapped)
                new_char = chr(ord('a') + (idx + 2) % 26) if swapped.islower() else chr(ord('A') + (idx + 2) % 26)
                result.append(new_char)
            else:
                result.append(swapped)
        else:
            result.append(char)
    return ''.join(result)

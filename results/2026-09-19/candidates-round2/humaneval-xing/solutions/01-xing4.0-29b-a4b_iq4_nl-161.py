def solve(s):
    letters = [ch for ch in s if ch.isalpha()]
    if not letters:
        return s[::-1]
    result = []
    for ch in s:
        if ch.isalpha():
            if ch.islower():
                result.append(ch.upper())
            else:
                result.append(ch.lower())
        else:
            result.append(ch)
    return ''.join(result)

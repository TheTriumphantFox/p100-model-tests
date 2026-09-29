def fix_spaces(text):
    result = []
    consecutive_count = 0
    for char in text:
        if char == ' ':
            consecutive_count += 1
            if consecutive_count <= 2:
                result.append('_')
        else:
            consecutive_count = 0
            result.append(char)
    return ''.join(result)

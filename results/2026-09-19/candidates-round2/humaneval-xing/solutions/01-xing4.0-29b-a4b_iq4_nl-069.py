def search(lst):
    from collections import Counter
    freq = Counter(lst)
    result = -1
    for num in sorted(set(lst), reverse=True):
        if freq[num] >= num:
            result = num
            break
    return result

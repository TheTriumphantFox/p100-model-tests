def strange_sort_list(lst):
    '''
    Given list of integers, return list in strange order.
    Strange sorting, is when you start with the minimum value,
    then maximum of the remaining integers, then minimum and so on.

    Examples:
    strange_sort_list([1, 2, 3, 4]) == [1, 4, 2, 3]
    strange_sort_list([5, 5, 5, 5]) == [5, 5, 5, 5]
    strange_sort_list([]) == []
    '''
    if not lst:
        return []

    sorted_lst = sorted(lst)
    result = []
    left = 0
    right = len(sorted_lst) - 1
    toggle = True  # True for min, False for max

    while left <= right:
        if toggle:
            result.append(sorted_lst[left])
            left += 1
        else:
            result.append(sorted_lst[right])
            right -= 1
        toggle = not toggle

    return result

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
    result = []
    left, right = 0, len(lst) - 1
    while left <= right:
        if left == right:
            result.append(lst[left])
            break
        if lst[left] <= lst[right]:
            result.append(lst[left])
            left += 1
        else:
            result.append(lst[right])
            right -= 1
    return result

def move_one_ball(arr):
    if not arr:
        return True
    n = len(arr)
    for i in range(n):
        shifted = arr[i:] + arr[:i]
        is_sorted = all(shifted[j] <= shifted[j+1] for j in range(n-1))
        if is_sorted:
            return True
    return False

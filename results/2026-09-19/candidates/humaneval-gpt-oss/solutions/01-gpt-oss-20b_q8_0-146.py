def specialFilter(nums):
    """
    Count numbers in the list that are greater than 10 and have both
    the first and last digits odd (1, 3, 5, 7, 9).

    Parameters
    ----------
    nums : list[int]
        List of integers to evaluate.

    Returns
    -------
    int
        The count of numbers satisfying the conditions.
    """
    odd_digits = {'1', '3', '5', '7', '9'}
    count = 0
    for n in nums:
        if n <= 10:
            continue
        s = str(n)
        if s[0] in odd_digits and s[-1] in odd_digits:
            count += 1
    return count

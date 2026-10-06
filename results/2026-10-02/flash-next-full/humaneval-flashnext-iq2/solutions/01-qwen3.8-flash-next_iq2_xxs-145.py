def order_by_points(nums):
    """
    Write a function which sorts the given list of integers
    in ascending order according to the sum of their digits.
    Note: if there are several items with similar sum of their digits,
    order them based on their index in original list.

    For example:
    >>> order_by_points([1, 11, -1, -11, -12]) == [-1, -11, 1, -12, 11]
    >>> order_by_points([]) == []
    """
    def digit_sum(n):
        s = 0
        n = abs(n)
        while n > 0:
            s += n % 10
            n //= 10
        return s
    
    # Create list of (digit_sum, index, value) tuples
    indexed_nums = [(digit_sum(x), i, x) for i, x in enumerate(nums)]
    
    # Sort by digit_sum, then by original index (stable sort preserves original order for ties)
    indexed_nums.sort(key=lambda x: x[0])
    
    # Extract the values in sorted order
    return [x[2] for x in indexed_nums]

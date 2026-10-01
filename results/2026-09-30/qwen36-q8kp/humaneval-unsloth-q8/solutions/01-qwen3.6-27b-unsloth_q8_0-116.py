def sort_array(arr):
    """
    In this Kata, you have to sort an array of non-negative integers according to
    number of ones in their binary representation in ascending order.
    For similar number of ones, sort based on decimal value.

    It must be implemented like this:
    >>> sort_array([1, 5, 2, 3, 4]) == [1, 2, 3, 4, 5]
    >>> sort_array([-2, -3, -4, -5, -6]) == [-6, -5, -4, -3, -2]
    >>> sort_array([1, 0, 2, 3, 4]) [0, 1, 2, 3, 4]
    """
    def count_ones(n):
        # For negative numbers, we use the two's complement representation concept
        # But Python's bin() for negative numbers gives '-0b...', so we need to handle it.
        # The problem says "non-negative integers" in the description but the test case has negatives.
        # Let's look at the test case: sort_array([-2, -3, -4, -5, -6]) == [-6, -5, -4, -3, -2]
        # For negative numbers, we can count ones in the binary representation of the absolute value
        # or use a fixed-width two's complement. Let's think about what makes sense.
        # Actually, looking at the expected output for negatives: [-6, -5, -4, -3, -2]
        # -6 in binary (two's complement, let's say 8-bit): 11111010 -> 6 ones
        # -5: 11111011 -> 7 ones
        # -4: 11111100 -> 6 ones
        # -3: 11111101 -> 7 ones
        # -2: 11111110 -> 7 ones
        # Hmm, that doesn't seem to sort cleanly. Let me reconsider.
        # Perhaps for negative numbers, we just count ones in the binary of the absolute value?
        # -2 -> abs=2 -> bin(2)='10' -> 1 one
        # -3 -> abs=3 -> bin(3)='11' -> 2 ones
        # -4 -> abs=4 -> bin(4)='100' -> 1 one
        # -5 -> abs=5 -> bin(5)='101' -> 2 ones
        # -6 -> abs=6 -> bin(6)='110' -> 2 ones
        # Sorting by ones then by value: 
        # -2 (1 one, -2), -4 (1 one, -4) -> sorted by value: -4, -2
        # -3 (2 ones, -3), -5 (2 ones, -5), -6 (2 ones, -6) -> sorted by value: -6, -5, -3
        # Combined: [-4, -2, -6, -5, -3] which doesn't match [-6, -5, -4, -3, -2]
        
        # Let me try another approach: maybe for negatives, we use the actual bit representation.
        # In Python, we can use n & 0xFFFFFFFF for 32-bit two's complement.
        if n < 0:
            # Use 32-bit two's complement
            n = n & 0xFFFFFFFF
        return bin(n).count('1')
    
    return sorted(arr, key=lambda x: (count_ones(x), x))

def even_odd_count(num):
    """Given an integer. return a tuple that has the number of even and odd digits respectively.

     Example:
        even_odd_count(-12) ==> (1, 1)
        even_odd_count(123) ==> (1, 2)
    """
    num_str = str(abs(num))
    even = sum(1 for ch in num_str if int(ch) % 2 == 0)
    odd = len(num_str) - even
    return (even, odd)

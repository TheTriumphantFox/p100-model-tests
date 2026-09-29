def even_odd_palindrome(n):
    even = 0
    odd = 0
    for i in range(1, n + 1):
        s = str(i)
        if s == s[::-1]:
            if i % 2 == 0:
                even += 1
            else:
                odd += 1
    return (even, odd)

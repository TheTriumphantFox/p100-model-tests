def is_multiply_prime(a):
    """Write a function that returns true if the given number is the multiplication of 3 prime numbers
    and false otherwise.
    Knowing that (a) is less then 100. 
    Example:
    is_multiply_prime(30) == True
    30 = 2 * 3 * 5
    """
    # Get all primes up to 100
    primes = []
    for num in range(2, 100):
        is_prime = True
        for i in range(2, int(num**0.5) + 1):
            if num % i == 0:
                is_prime = False
                break
        if is_prime:
            primes.append(num)
    
    # Check if a can be expressed as the product of exactly 3 primes
    # The primes don't have to be distinct
    for i in range(len(primes)):
        for j in range(len(primes)):
            for k in range(len(primes)):
                if primes[i] * primes[j] * primes[k] == a:
                    return True
    return False

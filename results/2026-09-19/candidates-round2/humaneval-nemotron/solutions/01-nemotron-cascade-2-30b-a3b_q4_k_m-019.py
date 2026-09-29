from typing import List

def sort_numbers(numbers: str) -> str:
    """Input is a space-delimited string of number words from 'zero' to 'nine'.
    Valid choices are 'zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine'.
    Return the string with numbers sorted from smallest to largest.
    """
    word_to_digit = {
        "zero": 0,
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
        "six": 6,
        "seven": 7,
        "eight": 8,
        "nine": 9,
    }
    words = numbers.split()
    sorted_words = sorted(words, key=lambda w: word_to_digit[w])
    return " ".join(sorted_words)

def valid_date(date):
    """You have to write a function which validates a given date string and
    returns True if the date is valid otherwise False.
    The date is valid if all of the following rules are satisfied:
    1. The date string is not empty.
    2. The number of days is not less than 1 or higher than 31 days for months 1,3,5,7,8,10,12. And the number of days is not less than 1 or higher than 30 days for months 4,6,9,11. And, the number of days is not less than 1 or higher than 29 for the month 2.
    3. The months should not be less than 1 or higher than 12.
    4. The date should be in the format: mm-dd-yyyy

    for example: 
    valid_date('03-11-2000') => True

    valid_date('15-01-2012') => False

    valid_date('04-0-2040') => False

    valid_date('06-04-2020') => True

    valid_date('06/04/2020') => False
    """
    if not date or not isinstance(date, str):
        return False
    
    # Check format: mm-dd-yyyy
    parts = date.split('-')
    if len(parts) != 3:
        return False
    
    mm_str, dd_str, yyyy_str = parts
    
    # Each part should be non-empty
    if not mm_str or not dd_str or not yyyy_str:
        return False
    
    # Check that all parts are digits
    if not mm_str.isdigit() or not dd_str.isdigit() or not yyyy_str.isdigit():
        return False
    
    # Check that mm and dd are exactly 2 digits and yyyy is exactly 4 digits
    if len(mm_str) != 2 or len(dd_str) != 2 or len(yyyy_str) != 4:
        return False
    
    mm = int(mm_str)
    dd = int(dd_str)
    yyyy = int(yyyy_str)
    
    # Check month range
    if mm < 1 or mm > 12:
        return False
    
    # Check day range based on month
    if mm in (1, 3, 5, 7, 8, 10, 12):
        if dd < 1 or dd > 31:
            return False
    elif mm in (4, 6, 9, 11):
        if dd < 1 or dd > 30:
            return False
    elif mm == 2:
        if dd < 1 or dd > 29:
            return False
    
    return True

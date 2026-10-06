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
    # Check if the date string is empty
    if not date:
        return False
    
    # Check if the date string contains only digits and hyphens
    if not all(c.isdigit() or c == '-' for c in date):
        return False
    
    # Split the date string by hyphens
    parts = date.split('-')
    
    # Check if there are exactly 3 parts
    if len(parts) != 3:
        return False
    
    # Check if each part is not empty
    if any(len(part) == 0 for part in parts):
        return False
    
    # Check if each part contains only digits
    if not all(part.isdigit() for part in parts):
        return False
    
    # Parse month, day, year
    try:
        month = int(parts[0])
        day = int(parts[1])
        year = int(parts[2])
    except ValueError:
        return False
    
    # Check month validity
    if month < 1 or month > 12:
        return False
    
    # Check day validity based on month
    if month in [1, 3, 5, 7, 8, 10, 12]:
        if day < 1 or day > 31:
            return False
    elif month in [4, 6, 9, 11]:
        if day < 1 or day > 30:
            return False
    elif month == 2:
        if day < 1 or day > 29:
            return False
    
    return True

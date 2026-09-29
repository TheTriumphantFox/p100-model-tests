def numerical_letter_grade(grades):
    """
    Convert a list of numeric GPAs to letter grades based on the provided table.

    Parameters
    ----------
    grades : list[float]
        List of GPA values.

    Returns
    -------
    list[str]
        Corresponding list of letter grades.
    """
    result = []
    for gpa in grades:
        if gpa == 4.0:
            result.append("A+")
        elif gpa > 3.7:
            result.append("A")
        elif gpa > 3.3:
            result.append("A-")
        elif gpa > 3.0:
            result.append("B+")
        elif gpa > 2.7:
            result.append("B")
        elif gpa > 2.3:
            result.append("B-")
        elif gpa > 2.0:
            result.append("C+")
        elif gpa > 1.7:
            result.append("C")
        elif gpa > 1.3:
            result.append("C-")
        elif gpa > 1.0:
            result.append("D+")
        elif gpa > 0.7:
            result.append("D")
        elif gpa > 0.0:
            result.append("D-")
        else:
            result.append("E")
    return result

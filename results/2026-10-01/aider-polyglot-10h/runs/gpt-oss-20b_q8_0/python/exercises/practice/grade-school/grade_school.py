class School:
    def __init__(self):
        # Internal mapping from grade number to a set of student names
        self._grades = {}
        # Keep track of the result of each add_student call
        self._add_results = []

    def add_student(self, name, grade):
        """
        Add a student to a specific grade.

        :param name: str, the student's name
        :param grade: int, the grade number
        :return: bool, True if the student was added, False if the student was already in the grade
        """
        if grade not in self._grades:
            self._grades[grade] = set()

        if name in self._grades[grade]:
            self._add_results.append(False)
            return False

        self._grades[grade].add(name)
        self._add_results.append(True)
        return True

    def roster(self, grade=None):
        """
        Return a sorted list of students.

        If a grade is provided, return the students in that grade sorted alphabetically.
        If no grade is provided, return all students sorted first by grade (ascending)
        and then alphabetically within each grade.

        :param grade: int or None
        :return: list of student names
        """
        if grade is None:
            all_students = []
            for g in sorted(self._grades):
                all_students.extend(sorted(self._grades[g]))
            return all_students

        if grade not in self._grades:
            return []

        return sorted(self._grades[grade])

    def grade(self, grade_number):
        """
        Alias for roster – returns the list of students in a grade.

        :param grade_number: int, the grade number
        :return: list of student names sorted alphabetically
        """
        return self.roster(grade_number)

    def added(self):
        """
        Return a list of booleans indicating the success of each add_student call.

        :return: list of bool
        """
        return self._add_results

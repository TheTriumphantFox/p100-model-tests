class School:
    def __init__(self):
        self._grades = {}
        self._added = []

    def add_student(self, name, grade):
        if name in [student for students in self._grades.values() for student in students]:
            self._added.append(False)
            return False
        if grade not in self._grades:
            self._grades[grade] = []
        self._grades[grade].append(name)
        self._grades[grade].sort()
        self._added.append(True)
        return True

    def roster(self):
        roster = []
        for grade in sorted(self._grades.keys()):
            roster.extend(self._grades[grade])
        return roster

    def grade(self, grade_number):
        return self._grades.get(grade_number, [])

    def added(self):
        return self._added

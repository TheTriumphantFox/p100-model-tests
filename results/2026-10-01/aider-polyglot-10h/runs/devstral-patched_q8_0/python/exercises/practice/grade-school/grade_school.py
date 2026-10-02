class School:
    def __init__(self):
        self.grades = {}
        self.added_results = []

    def add_student(self, name, grade):
        # Check if student already exists in any grade
        for existing_grade in self.grades:
            if name in self.grades[existing_grade]:
                self.added_results.append(False)
                return False

        # Check if student already exists in this specific grade
        if name in self.grades.get(grade, []):
            self.added_results.append(False)
            return False

        if grade not in self.grades:
            self.grades[grade] = []
        self.grades[grade].append(name)
        self.added_results.append(True)
        return True

    def roster(self):
        sorted_grades = sorted(self.grades.keys())
        roster = []
        for grade in sorted_grades:
            roster.extend(sorted(self.grades[grade]))
        return roster

    def grade(self, grade_number):
        if grade_number in self.grades:
            return sorted(self.grades[grade_number])
        return []

    def added(self):
        return self.added_results

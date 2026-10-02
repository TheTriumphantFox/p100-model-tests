class School:
    def __init__(self):
        self.students = {}
        self.added_students = set()
        self.add_results = []

    def add_student(self, name, grade):
        if name in self.added_students:
            self.add_results.append(False)
            return False
        self.added_students.add(name)
        if grade not in self.students:
            self.students[grade] = []
        self.students[grade].append(name)
        self.add_results.append(True)
        return True

    def roster(self):
        all_students = []
        for grade in sorted(self.students.keys()):
            all_students.extend(sorted(self.students[grade]))
        return all_students

    def grade(self, grade_number):
        if grade_number in self.students:
            return sorted(self.students[grade_number])
        return []

    def added(self):
        return self.add_results.copy()

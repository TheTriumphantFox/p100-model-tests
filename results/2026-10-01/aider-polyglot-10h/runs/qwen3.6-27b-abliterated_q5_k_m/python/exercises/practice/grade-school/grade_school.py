class School:
    def __init__(self):
        self._roster = {}
        self._added_students = set()
        self._add_results = []

    def add_student(self, name, grade):
        if name in self._added_students:
            self._add_results.append(False)
            return False
        
        if grade not in self._roster:
            self._roster[grade] = []
        
        self._roster[grade].append(name)
        self._added_students.add(name)
        self._add_results.append(True)
        return True

    def roster(self):
        result = []
        for grade in sorted(self._roster.keys()):
            result.extend(sorted(self._roster[grade]))
        return result

    def grade(self, grade_number):
        if grade_number in self._roster:
            return sorted(self._roster[grade_number])
        return []

    def added(self):
        return list(self._add_results)

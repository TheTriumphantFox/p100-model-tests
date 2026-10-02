class School:
    def __init__(self):
        self._roster = {}
        self._added_log = []

    def add_student(self, name, grade):
        for existing_roster in self._roster.values():
            if name in existing_roster:
                self._added_log.append(False)
                return
        
        if grade not in self._roster:
            self._roster[grade] = []
        self._roster[grade].append(name)
        self._added_log.append(True)

    def roster(self):
        students = []
        for grade in sorted(self._roster.keys()):
            students.extend(sorted(self._roster[grade]))
        return students

    def grade(self, grade_number):
        if grade_number in self._roster:
            return sorted(self._roster[grade_number])
        return []

    def added(self):
        return self._added_log

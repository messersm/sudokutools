class RemoveCandidates(object):
    def __init__(self, coordinates, candidates):
        self.coordinates = coordinates
        self.candidates = candidates

    def __call__(self, sudoku):
        for row, col in self.coordinates:
            sudoku.remove_candidates(row, col, self.candidates)

    def __str__(self):
        return "RemoveCandidates(%s, %s)" % (
            self.coordinates, self.candidates)


class SetNumber(object):
    def __init__(self, coordinates, number):
        self.coordinates = coordinates
        self.number = number

    def __call__(self, sudoku):
        for row, col in self.coordinates:
            sudoku.set_number(row, col, self.number)

    def __str__(self):
        return "SetNumber(%s, %s)" % (
            self.coordinates, self.number)

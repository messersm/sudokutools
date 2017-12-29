from collections import defaultdict
from itertools import combinations
import string

# local imports
import coord

class Sudoku(object):
    def __init__(self):
        self.numbers = []
        for i in range(9):
            self.numbers.append([0] * 9)

        self.candidates = []
        for i in range(9):
            self.candidates.append([set() for i in range(9)])

    def __getitem__(self, row):
        return self.numbers[row]

    def __str__(self):
        """Return a string representation of this sudoku

        Example:
        >>> sudoku = Sudoku()
        >>> sudoku[4][2] = 7
        >>> print(sudoku)
        000000000
        000000000
        000000000
        000000000
        007000000
        000000000
        000000000
        000000000
        000000000
        """

        rows = ["".join([str(x) for x in row]) for row in self.numbers]
        return "\n".join(rows)

    @property
    def empty(self):
        return [(i, j) for i in range(9) for j in range(9) if self[i][j] == 0]

    @classmethod
    def from_str(cls, s, empty='0'):
        """Return a sudoku from string s"""
        # remove whitespace
        s = s.translate(None, string.whitespace)
        if len(s) != 81:
            raise ValueError(
                "Expected string with exactly 81 non-whitespace characters.")

        row = 0
        col = 0
        sudoku = cls()

        for c in s:
            if c == empty:
                sudoku[row][col] = 0
            else:
                sudoku[row][col] = int(c)

            col += 1
            if col >= 9:
                row += 1
                col = 0

        return sudoku

def init_candidates(sudoku):
    for row in range(9):
        for col in range(9):
            value = sudoku[row][col]
            if value:
                sudoku.candidates[row][col] = {value}
                continue

            c = {1, 2, 3, 4, 5, 6, 7, 8, 9}
            for (i, j) in coord.surrounding(row, col, include=False):
                try:
                    c.remove(sudoku[i][j])
                except KeyError:
                    pass
            sudoku.candidates[row][col] = c
            print("(%d, %d) Set candidates: %s" % (row, col, str(c)))


def solve_naked_singles(sudoku):
    for row, col in sudoku.empty:
        c = sudoku.candidates[row][col]
        if len(c) == 1:
            # for rationale see:
            # https://stackoverflow.com/questions/59825/how-to-retrieve-an-element-from-a-set-without-removing-it
            for val in c:
                sudoku[row][col] = val
                break


def solve_naked_singles_at(sudoku, coords):
    for row, col in coords:
        c = sudoku.candidates[row][col]
        if len(c) == 1:
            # for rationale see:
            # https://stackoverflow.com/questions/59825/how-to-retrieve-an-element-from-a-set-without-removing-it
            for val in c:
                break
            sudoku[row][col] = val

            for i, j in coord.surrounding(row, col, include=False):
                try:
                    sudoku.candidates[row][col].remove(val)
                except:
                    pass


def solve_naked_n(sudoku, n=2):
    # we work through rows, cols and quads in 3 steps, since the
    # empty fields can changed in-between
    for func in coord.row, coord.col, coord.quad:
        clist = []
        for (i, j) in sudoku.empty:
            coords = func(i, j)
            if coords not in clist:
                clist.append(coords)
        for coords in clist:
            solve_naked_n_at(sudoku, coords, n=n)


def solve_naked_n_at(sudoku, coords, n=2):
    # Create a list of fields with at least 2 and at most n candidates.
    # (We ignore naked singles here, because combinations() would
    # return a very long list otherwise.)
    n_candidates = [(row, col) for (row, col) in coords if 1 < len(
        sudoku.candidates[row][col]) <= n]

    for fields in combinations(n_candidates, n):
        all_candidates = set()
        for (row, col) in fields:
            all_candidates |= sudoku.candidates[row][col]

        if len(all_candidates) <= n:
            # Remove all candidates in max_candidates
            # from the coordinates, which are not in fields.
            for (row, col) in coords:
                if (row, col) not in fields:
                    sudoku.candidates[row][col] -= all_candidates # APPLY
                    print("(%d, %d) Remove candidates: %s" % (
                        row, col, str(all_candidates)))


def solve_hidden_singles(sudoku):
    # we work through rows, cols and quads in 3 steps, since the
    # empty fields can changed in-between
    for func in coord.row, coord.col, coord.quad:
        clist = []
        for (i, j) in sudoku.empty:
            coords = func(i, j)
            if coords not in clist:
                clist.append(coords)
        for coords in clist:
            solve_hidden_singles_at(sudoku, coords)


def solve_hidden_singles_at(sudoku, coords):
    cand_coords = defaultdict(lambda: list())

    # build coordinate list for each candidate
    for n in range(1, 10):
        for (row, col) in coords:
            if n in sudoku.candidates[row][col]:
                cand_coords[n].append((row, col))

    # check, if there are candidates with only one coord
    # and set them, if this is the case
    for n in range(1, 10):
        if len(cand_coords[n]) == 1:
            row, col = cand_coords[n][0]
            sudoku[row][col] = n        # This is also done by naked_single
            sudoku.candidates[row][col] = {n}


def solve_hidden_n(sudoku, n=2):
    # we work through rows, cols and quads in 3 steps, since the
    # empty fields can changed in-between
    for func in coord.row, coord.col, coord.quad:
        clist = []
        for (i, j) in sudoku.empty:
            coords = func(i, j)
            if coords not in clist:
                clist.append(coords)
        for coords in clist:
            solve_hidden_n_at(sudoku, coords, n=n)


def solve_hidden_n_at(sudoku, coords, n=2):
    cand_coords = defaultdict(lambda: set())

    # build coordinate list for each candidate
    for cand in range(1, 10):
        for (row, col) in coords:
            if cand in sudoku.candidates[row][col]:
                cand_coords[cand].add((row, col))

    # create a list of numbers with at most n occurrences
    n_times = [cand for cand in range(1, 10) if 1 < len(cand_coords[cand]) <= n]

    # select n numbers from the n_times list
    for numbers in combinations(n_times, n):
        max_set = set()
        for num in numbers:
            max_set |= cand_coords[num]

        if len(max_set) <= n:
            # remove all candidates, which are not in numbers from max_set
            numbers = set(numbers)
            for (row, col) in max_set:
                sudoku.candidates[row][col] &= numbers


def solve(sudoku):
    init_candidates(sudoku)

    empty = sudoku.empty
    empty_len = len(empty)

    while empty:
        solve_naked_singles(sudoku)
        solve_hidden_singles(sudoku)
        for n in range(2, 5):
            solve_naked_n(sudoku, n)
            solve_hidden_n(sudoku, n)

        empty = sudoku.empty
        if len(empty) == empty_len:
            print("No more solutions...")
            return
        else:
            empty_len = len(empty)


if __name__ == '__main__':
    from printing import pretty_str

    s = """
    049132000
    081479000
    327685914
    096051800
    075028000
    038046005
    853267000
    712894563
    964513000
    """

    s2 = """
    280000473
    534827196
    071034080
    300500040
    000340060
    460790310
    090203654
    003009821
    000080937
    """

    s3 = """
    010002000
    090060058
    007050200
    400000000
    026070140
    000000003
    002090600
    750010020
    000800090
    """

    # sudoku = Sudoku.from_str(s)
    # init_candidates(sudoku)
    # print(pretty_str(sudoku))
    # print("")
    # for (row, col) in coord.col(0, 8):
    #     print(sudoku[row][col])
    # solve_hidden_n_at(sudoku, coord.col(0, 8), n=2)
    # print(pretty_str(sudoku))

    # import sys
    # sys.exit(0)

    # triple
    # sudoku2 = Sudoku.from_str(s2, empty='.')
    # init_candidates(sudoku2)

    # for row, col in coord.quad(8, 0):
        # print(sudoku2[row][col])

    # print(pretty_str(sudoku2))
    # solve_hidden_n_at(sudoku2, coord.quad(8, 0), n=3)
    # print("")
    # print("###")
    # print("")
    # print(pretty_str(sudoku2))

    sudoku = Sudoku.from_str(s3)
    print(pretty_str(sudoku))
    solve(sudoku)
    print(pretty_str(sudoku))

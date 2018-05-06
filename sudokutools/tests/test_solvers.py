from unittest import TestCase

from sudokutools.solve import init_candidates
from sudokutools.solvers import Action, NakedSingle, HiddenSingle, Bruteforce
from sudokutools.sudoku import Sudoku

# Example for NakedSingle and HiddenSingle
SINGLES_EXAMPLE = """
090000070
006070000
070340000
030897000
000004507
000000600
000002009
800500460
003001005
"""

NAKED_SINGLE_STEPS = {
    NakedSingle(7, 4, 3),
}

HIDDEN_SINGLE_STEPS = {
    HiddenSingle(3, 0, 6),
    HiddenSingle(7, 2, 7)
}

BRUTEFORCE_EXAMPLE = """
182940560
650178923
073256418
421030875
367815290
895724136
210587349
708491652
549062701
"""

BRUTEFORCE_STEPS = {
    Bruteforce(0, 5, 3),
    Bruteforce(0, 8, 7),
    Bruteforce(1, 2, 4),
    Bruteforce(2, 0, 9),
    Bruteforce(3, 3, 6),
    Bruteforce(3, 5, 9),
    Bruteforce(4, 8, 4),
    Bruteforce(6, 2, 6),
    Bruteforce(7, 1, 3),
    Bruteforce(8, 3, 3),
    Bruteforce(8, 7, 8),
}


class StepTests(TestCase):
    def test_naked_single(self):
        sudoku = Sudoku.decode(SINGLES_EXAMPLE)
        init_candidates(sudoku)
        steps = set(NakedSingle.find(sudoku))
        self.assertEqual(steps, NAKED_SINGLE_STEPS)

    def test_hidden_single(self):
        sudoku = Sudoku.decode(SINGLES_EXAMPLE)
        init_candidates(sudoku)
        steps = set(HiddenSingle.find(sudoku))
        self.assertEqual(steps, HIDDEN_SINGLE_STEPS)

    def test_bruteforce(self):
        """Bruteforce finds all field values in a given example."""
        sudoku = Sudoku.decode(BRUTEFORCE_EXAMPLE)
        steps = set(Bruteforce.find(sudoku))
        self.assertEqual(steps, BRUTEFORCE_STEPS)

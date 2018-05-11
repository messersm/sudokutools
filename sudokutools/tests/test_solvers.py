from unittest import TestCase

from sudokutools.solve import init_candidates
from sudokutools.solvers import (
    NakedSingle, NakedPair, NakedTriple, NakedQuad, NakedQuint,
    HiddenSingle,
    Bruteforce
)
from sudokutools.sudoku import Sudoku, row_of, square_of, column_of

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

NAKED_SINGLE_STEPS = [
    NakedSingle(7, 4, 3),
]

HIDDEN_SINGLE_STEPS = [
    HiddenSingle(3, 0, 6),
    HiddenSingle(7, 2, 7)
]

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

BRUTEFORCE_STEPS = [
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
]


NAKED_PAIR_EXAMPLE = """
079008020
000000007
005021060
000040900
050300008
200000000
030002000
080050000
000090073
"""

NAKED_PAIR_STEPS = [
    NakedPair(((0, 4), (1, 4)), column_of(0, 4), (3, 6))
]

MORE_TUPLES_EXAMPLE = """
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

NAKED_TRIPLE_STEPS = [
    NakedTriple(((0, 3), (4, 3), (5, 3)), column_of(0, 3), (1, 2, 6)),
    NakedTriple(((3, 6), (3, 7), (3, 8)), row_of(3, 0), (1, 2, 4))
]

NAKED_QUAD_STEPS = [
    NakedQuad(((0, 3), (1, 3), (4, 3), (5, 3)), column_of(0, 3), (1, 2, 6, 9)),
    NakedQuad(((3, 2), (3, 6), (3, 7), (3, 8)), row_of(3, 0), (1, 2, 4, 5))
]

NAKED_QUINT_EXAMPLE = """
400305020
908010000
000000000
003000062
500020000
080700000
700000500
005003004
000408103
"""


NAKED_QUINT_STEPS = [
    NakedQuint(
        ((1, 3), (2, 3), (4, 3), (6, 3), (7, 3)),
        ((0, 3), (1, 3), (2, 3), (3, 3), (4, 3), (5, 3), (6, 3), (7, 3), (8, 3)),
        (1, 2, 6, 8, 9)),
    NakedQuint(
        ((6, 2), (7, 1), (8, 0), (8, 1), (8, 2)),
        ((6, 0), (6, 1), (6, 2), (7, 0), (7, 1), (7, 2), (8, 0), (8, 1), (8, 2)),
        (1, 2, 4, 6, 9)),
    NakedQuint(
        ((6, 3), (6, 4), (6, 5), (6, 7), (6, 8)),
        ((6, 0), (6, 1), (6, 2), (6, 3), (6, 4), (6, 5), (6, 6), (6, 7), (6, 8)),
        (1, 2, 6, 8, 9)),
    NakedQuint(
        ((6, 3), (6, 4), (6, 5), (7, 3), (7, 4)),
        ((6, 3), (6, 4), (6, 5), (7, 3), (7, 4), (7, 5), (8, 3), (8, 4), (8, 5)),
        (1, 2, 6, 7, 9)),
    NakedQuint(
        ((7, 0), (7, 1), (8, 0), (8, 1), (8, 2)),
        ((6, 0), (6, 1), (6, 2), (7, 0), (7, 1), (7, 2), (8, 0), (8, 1), (8, 2)),
        (1, 2, 6, 8, 9))
]


class StepTests(TestCase):
    def test_naked_single(self):
        sudoku = Sudoku.decode(SINGLES_EXAMPLE)
        init_candidates(sudoku)
        steps = sorted(NakedSingle.find(sudoku))
        self.assertEqual(steps, NAKED_SINGLE_STEPS)

    def test_naked_pair(self):
        sudoku = Sudoku.decode(NAKED_PAIR_EXAMPLE)
        init_candidates(sudoku)
        steps = sorted(NakedPair.find(sudoku))
        self.assertEqual(steps, NAKED_PAIR_STEPS)

    def test_naked_triple(self):
        sudoku = Sudoku.decode(MORE_TUPLES_EXAMPLE)
        init_candidates(sudoku)
        steps = sorted(NakedTriple.find(sudoku))
        self.assertEqual(steps, NAKED_TRIPLE_STEPS)

    def test_naked_quad(self):
        sudoku = Sudoku.decode(MORE_TUPLES_EXAMPLE)
        init_candidates(sudoku)
        steps = sorted(NakedQuad.find(sudoku))
        self.assertEqual(steps, NAKED_QUAD_STEPS)

    def test_naked_quint(self):
        sudoku = Sudoku.decode(NAKED_QUINT_EXAMPLE)
        init_candidates(sudoku)
        steps = sorted(NakedQuint.find(sudoku))
        self.assertEqual(steps, NAKED_QUINT_STEPS)

    def test_hidden_single(self):
        sudoku = Sudoku.decode(SINGLES_EXAMPLE)
        init_candidates(sudoku)
        steps = sorted(HiddenSingle.find(sudoku))
        self.assertEqual(steps, HIDDEN_SINGLE_STEPS)

    def test_bruteforce(self):
        """Bruteforce finds all field values in a given example."""
        sudoku = Sudoku.decode(BRUTEFORCE_EXAMPLE)
        steps = sorted(Bruteforce.find(sudoku))
        self.assertEqual(steps, BRUTEFORCE_STEPS)
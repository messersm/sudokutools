from unittest import TestCase

from sudokutools.solve import init_candidates
from sudokutools.solvers import (
    NakedSingle, NakedPair, NakedTriple, NakedQuad, NakedQuint,
    HiddenSingle, HiddenPair, HiddenTriple, HiddenQuad, HiddenQuint,
    Bruteforce
)
from sudokutools.sudoku import Sudoku

# A example sudoku covering all of the solve methods.
EXAMPLE = """
000070005
600051807
000800040
002000301
010002000
030000090
509000012
800000406
004006000
"""

FIRST_STEPS = [
    NakedSingle(1, 2, 3),
    NakedPair(
        ((2, 5), (2, 8)),
        ((2, 0), (2, 1), (2, 2), (2, 3), (2, 4), (2, 5), (2, 6), (2, 7), (2, 8)),
        (3, 9)),
    NakedTriple(
        ((3, 0), (4, 0), (5, 0)),
        ((0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0), (8, 0)),
        (4, 7, 9)),
    NakedQuad(
        ((7, 1), (7, 2), (8, 0), (8, 1)),
        ((6, 0), (6, 1), (6, 2), (7, 0), (7, 1), (7, 2), (8, 0), (8, 1), (8, 2)),
        (1, 2, 3, 7)),
    NakedQuint(
        ((3, 7), (4, 6), (4, 7), (4, 8), (5, 8)),
        ((3, 6), (3, 7), (3, 8), (4, 6), (4, 7), (4, 8), (5, 6), (5, 7), (5, 8)),
        (4, 5, 6, 7, 8)),
    HiddenSingle(5, 6, 2),
    HiddenPair(
        ((0, 8), (1, 8), (2, 8), (3, 8), (4, 8), (5, 8), (6, 8), (7, 8), (8, 8)),
        ((2, 8), (8, 8)),
        (3, 9)),
    HiddenTriple(
        ((0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0), (8, 0)),
        ((0, 0), (2, 0), (8, 0)),
        (1, 2, 3)),
    HiddenQuad(
        ((0, 1), (1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1), (8, 1)),
        ((0, 1), (1, 1), (2, 1), (3, 1)),
        (4, 5, 8, 9)),
    HiddenQuint(
        ((0, 1), (1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1), (8, 1)),
        ((0, 1), (1, 1), (2, 1), (3, 1), (6, 1)),
        (4, 5, 6, 8, 9)),
    Bruteforce(0, 0, 1),
]


class StepTests(TestCase):
    def test_first(self):
        sudoku = Sudoku.decode(EXAMPLE)
        init_candidates(sudoku)
        for first in FIRST_STEPS:
            cls = first.__class__
            steps = sorted(cls.find(sudoku))[:1]
            self.assertEqual(steps, [first], cls.__name__)

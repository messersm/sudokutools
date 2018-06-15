from unittest import TestCase

from sudokutools.generate import generate
from sudokutools.solve import init_candidates
from sudokutools.solvers import (
    NakedSingle, NakedPair, NakedTriple, NakedQuad, NakedQuint,
    HiddenSingle, HiddenPair, HiddenTriple, HiddenQuad, HiddenQuint,
    PointingPair, PointingTriple,
    XWing, Swordfish, Jellyfish,
    Bruteforce,
    SOLVERS
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
    PointingPair(
        ((0, 7), (1, 7)),
        ((0, 6), (0, 7), (0, 8), (1, 6), (1, 7), (1, 8), (2, 6), (2, 7), (2, 8)),
        (2,)),
    PointingTriple(
        ((6, 3), (6, 4), (6, 5)),
        ((6, 3), (6, 4), (6, 5), (7, 3), (7, 4), (7, 5), (8, 3), (8, 4), (8, 5)),
        (3,)),
    Bruteforce(0, 0, 1),
]

TEST_SIZES = ((2, 2), (2, 3), (2, 4), (3, 3), (4, 4))

XWING_EXAMPLE = """
500010070
840000000
603500000
000030005
000107000
030040210
070950400
000004502
000000900
"""

XWINGS = [
    XWing(((4, 1), (4, 2), (8, 1), (8, 2)), ((5, 2),), (5,)),
]

SWORDFISH_EXAMPLE = """
000190000
040270000
000005007
005683104
021700000
000000905
708012000
200000009
030800050
"""

SWORDFISHES = [
    Swordfish(((0, 1), (0, 2), (3, 1), (3, 7), (5, 1), (5, 2), (5, 7)), ((7, 7), ), (7,)),
    Swordfish(((0, 2), (0, 6), (0, 8), (2, 2), (2, 6), (8, 6), (8, 8)), ((0, 7), (2, 7)), (2,))
]

JELLYFISH_EXAMPLE = SWORDFISH_EXAMPLE

JELLYFISHES = [
    Jellyfish(((0, 0), (0, 1), (0, 6), (1, 0), (1, 6), (6, 1), (6, 3), (7, 1), (7, 3)), ((7, 4),), (5,))
]

class BasicTests(TestCase):
    def test_simple(self):
        """Naked Singles/Tuples, Hidden Singles/Tuples and pointing pairs work.
        """
        sudoku = Sudoku.decode(EXAMPLE)
        init_candidates(sudoku)
        for first in FIRST_STEPS:
            cls = first.__class__
            steps = sorted(cls.find(sudoku))[:1]
            self.assertEqual(steps, [first], cls.__name__)

    def test_sizes(self):
        """Finding solve steps doesn't raise an exception on different sizes."""
        for width, height in TEST_SIZES:
            count = (width ** 2 * height ** 2) // 2
            sudoku = generate(min_count=count, size=(width, height))

            for cls in SOLVERS:
                try:
                    steps = list(cls.find(sudoku))
                except Exception as e:
                    self.fail("%s.find() failed with: %s" %(
                        cls.__name__, str(e)))


class BasicFishTests(TestCase):
    def test_xwing(self):
        """XWing works."""
        sudoku = Sudoku.decode(XWING_EXAMPLE)
        init_candidates(sudoku)
        xwings = list(XWing.find(sudoku))
        self.assertEqual(xwings, XWINGS)

    def test_swordfish(self):
        """Swordfishes are found correctly."""
        sudoku = Sudoku.decode(SWORDFISH_EXAMPLE)
        init_candidates(sudoku)
        swordfishes = list(Swordfish.find(sudoku))
        self.assertEqual(swordfishes, SWORDFISHES)

    def test_jellyfish(self):
        """Jellyfishes are found correctly."""
        sudoku = Sudoku.decode(JELLYFISH_EXAMPLE)
        init_candidates(sudoku)
        jellyfishes = list(Jellyfish.find(sudoku))
        self.assertEqual(jellyfishes, JELLYFISHES)

from itertools import product
from unittest import TestCase

from sudokutools.solve import (
    bruteforce, find_conflicts, is_unique, calc_candidates, init_candidates
)
from sudokutools.sudoku import Sudoku, INDICES

SOLVE_EXAMPLES = [
    ("""
    003020600
    900305001
    001806400
    008102900
    700000008
    006708200
    002609500
    800203009
    005010300
    """, """
    483921657
    967345821
    251876493
    548132976
    729564138
    136798245
    372689514
    814253769
    695417382
    """),

    ("""
    009003008
    010040020
    200700400
    800600700
    090070010
    003004002
    005001007
    030090050
    700400200
    """, """
    469523178
    317948526
    258716439
    821659743
    694372815
    573184962
    945261387
    132897654
    786435291
    """),
    ("""
    000000000
    000008435
    000030860
    000000218
    060000000
    900154000
    001000040
    008700021
    020900500
    """, """
    835476192
    716298435
    249531867
    574369218
    163827954
    982154673
    351682749
    698745321
    427913586
    """),
]

CONFLICT_EXAMPLE = """
003020600
900305001
001806400
008102900
700000008
006708200
002609500
800203009
005010300
"""

NON_UNIQUE = """
000000000
000000000
000070000
000000000
000000000
000000000
000000000
000000000
000000000
"""

CANDIDATES_EXAMPLE = """
003020600
900305001
001806400
008102900
700000008
006708200
002609500
800203009
005010300|
45,4578,347,49,2479,147,678,5789,57,
2469,24678,47,34,47,457,78,278,127,
25,257,17,89,79,67,47,23579,2357,
345,345,48,145,3456,24,79,34567,34567,
123457,123459,49,459,34569,4,1,13456,34568,
1345,13459,469,4579,3459,48,12,1345,345,
134,1347,247,46,478,479,1578,1478,47,
1468,1467,47,245,457,347,17,1467,4679,
46,4679,4579,4,1478,47,378,24678,2467
"""


class BruteforceTests(TestCase):
    def test_examples(self):
        """Bruteforce solves the unique examples above.
        Running bruteforce in reverse still solves the examples above.
        """
        for example, solution in SOLVE_EXAMPLES:
            sudoku = Sudoku.decode(example)
            sol1 = bruteforce(sudoku)
            sol2 = bruteforce(sudoku, reverse=True)

            for c in "\n\t ":
                solution = solution.replace(c, '')
            self.assertEqual(sol1.encode(), solution)
            self.assertEqual(sol2.encode(), solution)

    def test_returns_solution(self):
        """If bruteforce solves a sudoku, it returns the solution.
        However: bruteforce may or may not solve a sudoku,
        which already has conflicts!
        """
        sudoku = Sudoku.decode(SOLVE_EXAMPLES[0][0])
        solution = bruteforce(sudoku)
        self.assertNotEqual(solution, None)
        self.assertEqual(len(solution), 81)

    def test_returns_false(self):
        """Bruteforce doesn't solve a sudoku, which cannot be solved.
        If bruteforce doesn't solve a sudoku it returns None.
        """

        sudoku = Sudoku.decode(SOLVE_EXAMPLES[0][0])
        sudoku[0, 0] = 5
        self.assertEqual(bruteforce(sudoku), None)

    def test_reverse_on_non_unique(self):
        """Running bruteforce in reverse order, produces another solution
        on non-unique sudokus.
        """
        sudoku = Sudoku.decode(NON_UNIQUE)
        sol1 = bruteforce(sudoku, reverse=False)
        sol2 = bruteforce(sudoku, reverse=True)
        self.assertNotEqual(sol1, sol2)


class CandidatesTest(TestCase):
    def test_calc_candidates_in_example(self):
        """

        Returns:

        """
        sudoku1 = Sudoku.decode(CANDIDATES_EXAMPLE)
        sudoku2 = sudoku1.copy(include_candidates=False)

        for row, col in product(INDICES, repeat=2):
            self.assertEqual(sudoku2.get_candidates(row, col), set())
            candidates = calc_candidates(sudoku2, row, col)
            self.assertEqual(sudoku1.get_candidates(row, col), candidates)

    def test_init_candidates(self):
        sudoku1 = Sudoku.decode(CANDIDATES_EXAMPLE)
        sudoku2 = sudoku1.copy()
        init_candidates(sudoku2)
        for row, col in product(INDICES, repeat=2):
            c1 = sudoku1.get_candidates(row, col)
            c2 = sudoku2.get_candidates(row, col)
            self.assertEqual(c1, c2)


class AnalyzeTests(TestCase):
    def setUp(self):
        """Makes sure, the example above is solvable."""
        self.assertNotEqual(bruteforce(Sudoku.decode(CONFLICT_EXAMPLE)), None)

    def test_find_conflicts_at(self):
        """The above example has no conflicts at (1, 2).
        Putting a 1 at (1, 2) creates a conflict at (1, 8) and (2, 2)
        and no other.
        """
        sudoku = Sudoku.decode(CONFLICT_EXAMPLE)
        self.assertEqual(list(find_conflicts(sudoku, (1, 2))), [])

        sudoku[1, 2] = 1

        conflicts = find_conflicts(sudoku, (1, 2))
        self.assertEqual(next(conflicts), ((1, 2), (1, 8), 1))
        self.assertEqual(next(conflicts), ((1, 2), (2, 2), 1))
        self.assertRaises(StopIteration, next, conflicts)

    def test_find_conflicts(self):
        """The above example has no conflicts.
        """
        sudoku = Sudoku.decode(CONFLICT_EXAMPLE)
        self.assertEqual(list(find_conflicts(sudoku)), [])

    def test_unique(self):
        """Every sudoku in SOLVE_EXAMPLES is unique.
        NON_UNIQUE is not unique.
        """

        for example, solution in SOLVE_EXAMPLES:
            sudoku = Sudoku.decode(example)
            self.assertEqual(is_unique(sudoku), True)

        sudoku = Sudoku.decode(NON_UNIQUE)
        self.assertEqual(is_unique(sudoku), False)

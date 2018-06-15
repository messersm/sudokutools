from itertools import product
from unittest import TestCase

from sudokutools.solve import (
    bruteforce, find_conflicts, is_unique, calc_candidates, init_candidates
)
from sudokutools.sudoku import Sudoku

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
    ("""
    123456
    630001
    500002
    462513
    314625
    251364
    """, """
    123456
    635241
    546132
    462513
    314625
    251364
    """)
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
45,4578,3,49,2,147,6,5789,57,
9,24678,47,3,47,5,78,278,1,
25,257,1,8,79,6,4,23579,2357,
345,345,8,1,3456,2,9,34567,34567,
7,123459,49,459,34569,4,1,13456,8,
1345,13459,6,7,3459,8,2,1345,345,
134,1347,2,6,478,9,5,1478,47,
8,1467,47,2,457,3,17,1467,9,
46,4679,5,4,1,47,3,24678,2467
"""

TEST_SIZES = ((2, 2), (2, 3), (2, 4), (3, 3), (4, 4))


class BruteforceTests(TestCase):
    def test_examples(self):
        """Bruteforce solves the given examples."""
        for example_str, solution_str in SOLVE_EXAMPLES:
            example = Sudoku.decode(example_str)
            solution = Sudoku.decode(solution_str)
            self.assertEqual(list(bruteforce(example))[0], solution)

    def test_examples_count(self):
        """Bruteforce yields exactly one solution to the given examples."""
        for example_str, solution_str in SOLVE_EXAMPLES:
            example = Sudoku.decode(example_str)
            solution = Sudoku.decode(solution_str)
            self.assertEqual(len(list(bruteforce(example))),1)

    def test_yields_nothing(self):
        """Bruteforce yields no solution, if a sudoku cannot be solved."""
        sudoku = Sudoku.decode(SOLVE_EXAMPLES[0][0])
        sudoku[0, 0] = 5
        self.assertEqual(len(list(bruteforce(sudoku))), 0)

    def test_reverse_on_non_unique(self):
        """Bruteforce yields multiple solutions on non-unique sudokus."""
        sudoku = Sudoku.decode(NON_UNIQUE)
        solutions = bruteforce(sudoku)
        sol1 = next(solutions)
        sol2 = next(solutions)
        self.assertNotEqual(sol1, sol2)


class CandidatesTest(TestCase):
    def test_calc_candidates_in_example(self):
        """Candidates in the given examples are calculated correctly."""
        sudoku1 = Sudoku.decode(CANDIDATES_EXAMPLE)
        sudoku2 = sudoku1.copy(include_candidates=False)

        for row, col in sudoku1:
            self.assertEqual(sudoku2.get_candidates(row, col), set())
            candidates = calc_candidates(sudoku2, row, col)
            self.assertEqual(sudoku1.get_candidates(row, col), candidates)

    def test_init_candidates(self):
        """Candidates in the given sudoku are calculated correctly."""
        sudoku1 = Sudoku.decode(CANDIDATES_EXAMPLE)
        sudoku2 = sudoku1.copy()
        init_candidates(sudoku2)
        for row, col in sudoku1:
            c1 = sudoku1.get_candidates(row, col)
            c2 = sudoku2.get_candidates(row, col)
            self.assertEqual(c1, c2)

    def test_init_candidates_filled_only(self):
        """The filled_only keyword argument of init_candidates() works."""

        sudoku = Sudoku.decode(CANDIDATES_EXAMPLE).copy()
        init_candidates(sudoku, filled_only=True)
        for row, col in sudoku:
            val = sudoku[row, col]
            if val:
                self.assertEqual(
                    sudoku.get_candidates(row, col), frozenset([val]))
            else:
                self.assertEqual(sudoku.get_candidates(row, col), frozenset())

    def test_number_candidates(self):
        """A number unequal to 0 in a field is the field's single candidate."""
        sudoku1 = Sudoku.decode(CANDIDATES_EXAMPLE)
        sudoku2 = sudoku1.copy()
        init_candidates(sudoku2)

        for row, col in sudoku1:
            value = sudoku1[row, col]
            if value:
                self.assertEqual(sudoku2.get_candidates(row, col), {value})


class AnalyzeTests(TestCase):
    def setUp(self):
        """The example provided by this unittest is solvable."""
        self.assertNotEqual(bruteforce(Sudoku.decode(CONFLICT_EXAMPLE)), None)

    def test_find_conflicts_at(self):
        """Conflicts at certain coordinates in a given example are found."""
        sudoku = Sudoku.decode(CONFLICT_EXAMPLE)
        self.assertEqual(list(find_conflicts(sudoku, (1, 2))), [])

        sudoku[1, 2] = 1

        conflicts = find_conflicts(sudoku, (1, 2))
        self.assertEqual(next(conflicts), ((1, 2), (1, 8), 1))
        self.assertEqual(next(conflicts), ((1, 2), (2, 2), 1))
        self.assertRaises(StopIteration, next, conflicts)

    def test_find_conflicts_sizes(self):
        """find_conflicts works with different sudoku sizes."""

        for size in TEST_SIZES:
            sudoku = Sudoku(size=size)
            self.assertEqual(list(find_conflicts(sudoku)), [])

        for example, solution in SOLVE_EXAMPLES:
            sudoku = Sudoku.decode(example)
            self.assertEqual(list(find_conflicts(sudoku)), [])

    def test_find_conflicts(self):
        """If a sudoku has no conflicts, none are found."""
        sudoku = Sudoku.decode(CONFLICT_EXAMPLE)
        self.assertEqual(list(find_conflicts(sudoku)), [])

    def test_unique(self):
        """If a sudoku is unique, it is evaluated as unique."""
        for example, solution in SOLVE_EXAMPLES:
            sudoku = Sudoku.decode(example)
            self.assertEqual(is_unique(sudoku), True)

    def test_non_unique(self):
        """If a sudoku is not unique, it is evaluated as non-unique."""
        sudoku = Sudoku.decode(NON_UNIQUE)
        self.assertEqual(is_unique(sudoku), False)

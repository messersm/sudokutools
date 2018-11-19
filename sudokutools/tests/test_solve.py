from unittest import TestCase

from sudokutools.analyze import find_conflicts
from sudokutools.generate import generate
from sudokutools.solve import bruteforce, dlx, calc_candidates, init_candidates
from sudokutools.sudoku import Sudoku

from sudokutools.tests.constants import SOLVE_EXAMPLES, NON_UNIQUE, UNSOLVABLES

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

    def test_unsolvable(self):
        """Bruteforce yields nothing on unsolvable sudokus."""
        for unsolvable in UNSOLVABLES:
            sudoku = Sudoku.decode(unsolvable)
            # make sure this sudoku has conflicts
            self.assertNotEqual(list(find_conflicts(sudoku)), [])
            self.assertEqual(list(bruteforce(sudoku)), [])


class DLXTests(TestCase):
    def test_examples(self):
        """DLX solves the given examples."""
        for example_str, solution_str in SOLVE_EXAMPLES:
            example = Sudoku.decode(example_str)
            solution = Sudoku.decode(solution_str)
            self.assertEqual(list(dlx(example))[0], solution)

    def test_examples_count(self):
        """DLX yields exactly one solution to the given examples."""
        for example_str, solution_str in SOLVE_EXAMPLES:
            example = Sudoku.decode(example_str)
            solution = Sudoku.decode(solution_str)
            self.assertEqual(len(list(dlx(example))),1)

    def test_yields_nothing(self):
        """DLX yields no solution, if a sudoku cannot be solved."""
        sudoku = Sudoku.decode(SOLVE_EXAMPLES[0][0])
        sudoku[0, 0] = 5
        self.assertEqual(len(list(dlx(sudoku))), 0)

    def test_reverse_on_non_unique(self):
        """DLX yields multiple solutions on non-unique sudokus."""
        sudoku = Sudoku.decode(NON_UNIQUE)
        solutions = dlx(sudoku)
        sol1 = next(solutions)
        sol2 = next(solutions)
        self.assertNotEqual(sol1, sol2)

    def test_unsolvable(self):
        """DLX yields nothing on unsolvable sudokus."""
        for unsolvable in UNSOLVABLES:
            sudoku = Sudoku.decode(unsolvable)
            # make sure this sudoku has conflicts
            self.assertNotEqual(list(find_conflicts(sudoku)), [])
            self.assertEqual(list(dlx(sudoku)), [])


class CompareTests(TestCase):
    def test_compare_with_bruteforce(self):
        """DLX yields the same solutions as bruteforce."""
        for i in range(10):
            sudoku = generate()
            self.assertEqual(next(bruteforce(sudoku)), next(dlx(sudoku)))


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

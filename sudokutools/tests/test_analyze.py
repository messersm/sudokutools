from unittest import TestCase

from sudokutools.analyze import (
    rate, RATINGS, find_conflicts, is_solved, is_unique, score)
from sudokutools.generate import create_solution, generate
from sudokutools.solve import bruteforce, init_candidates
from sudokutools.solvers import SOLVERS
from sudokutools.sudoku import Sudoku

from sudokutools.tests.constants import NON_UNIQUE, SOLVE_EXAMPLES, \
    TEST_SIZES


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


class ConflictTests(TestCase):
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


class IsSolvedTests(TestCase):
    def test_is_solved(self):
        """If a sudoku is solved, it is evaluated as solved."""
        solution = create_solution()
        sudoku = generate()
        self.assertEqual(is_solved(solution), True)
        self.assertEqual(is_solved(sudoku), False)


class IsUniqueTests(TestCase):
    def test_unique(self):
        """If a sudoku is unique, it is evaluated as unique."""
        for example, solution in SOLVE_EXAMPLES:
            sudoku = Sudoku.decode(example)
            self.assertEqual(is_unique(sudoku), True)

    def test_non_unique(self):
        """If a sudoku is not unique, it is evaluated as non-unique."""
        sudoku = Sudoku.decode(NON_UNIQUE)
        self.assertEqual(is_unique(sudoku), False)


class RatingTests(TestCase):
    def test_ratings_cover_solvers(self):
        """Each solve method has a rating."""
        for cls in SOLVERS:
            self.assertIn(cls, RATINGS, cls.__name__)
            self.assertIsInstance(RATINGS[cls], int, cls.__name__)

    def test_solved_rates_zero(self):
        """A solved sudoku rates as 0."""
        solution = create_solution()
        self.assertEqual(rate(solution), 0)

        # This will also return no CalculateCandidates step.
        init_candidates(solution)
        self.assertEqual(rate(solution), 0)

    def test_rate_works_on_random_sudoku(self):
        """A random sudoku is rated correctly."""
        sudoku = generate()
        rating = rate(sudoku)
        self.assertGreater(rating, 0)
        self.assertLessEqual(rating, 10)


class ScoreTests(TestCase):
    def test_solved_scores_zero(self):
        """A solved sudoku has a score of 0."""
        solution = create_solution()
        self.assertEqual(score(solution), 0)

        # This will also return no CalculateCandidates step.
        init_candidates(solution)
        self.assertEqual(score(solution), 0)

    def test_score_works_on_random_sudoku(self):
        """A random sudoku is scored correctly."""
        sudoku = generate()
        self.assertGreater(score(sudoku), 0)
        max_score = len(list(sudoku.empty())) * max(RATINGS.values())
        self.assertLessEqual(score(sudoku), max_score)


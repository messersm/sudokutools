from unittest import TestCase

from sudokutools.analyze import rate, RATINGS
from sudokutools.generate import create_solution, generate
from sudokutools.solvers import SOLVERS


class TestRate(TestCase):
    def test_ratings_cover_solvers(self):
        """Each solve method has a rating."""
        for cls in SOLVERS:
            self.assertIn(cls, RATINGS, cls.__name__)
            self.assertIsInstance(RATINGS[cls], int, cls.__name__)

    def test_solved_rates_zero(self):
        """A solved sudoku rates as 0."""
        solution = create_solution()
        self.assertEqual(rate(solution), 0)

    def test_rate_works_on_random_sudoku(self):
        """A random sudoku is rated correctly."""
        sudoku = generate()
        rating = rate(sudoku)
        self.assertGreater(rating, 0)
        self.assertLessEqual(rating, 10)

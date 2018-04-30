from unittest import TestCase

from sudokutools.generate import generate, create_solution
from sudokutools.solve import find_conflicts, is_unique


class CreateSolutionTests(TestCase):
    def test_created_solution_is_complete_and_correct(self):
        """A sudoku created by create_filled is complete
        and correct.
        """
        sudoku = create_solution()
        self.assertEqual(len(sudoku), 81)
        self.assertEqual(list(find_conflicts(sudoku)), [])


class GenerateTests(TestCase):
    def test_generated_is_solvable_and_unique(self):
        """A generated sudoku has no conflicts and is unique.
        A generated sudoku is unique.
        """
        for i in range(10):
            sudoku = generate()
            self.assertEqual(len(list(find_conflicts(sudoku))), 0)
            self.assertEqual(is_unique(sudoku), True)

    def test_generate_min(self):
        """A generated sudoku has at least the minimal number of filled fields
        that we specified.
        """
        for i in range(10):
            sudoku = generate(min_count=40)
            self.assertGreaterEqual(len(sudoku), 40)

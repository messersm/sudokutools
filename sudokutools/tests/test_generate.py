from itertools import product
from unittest import TestCase

from sudokutools.generate import (
    generate, generate_from_template, create_solution
)
from sudokutools.solve import find_conflicts, is_unique
from sudokutools.sudoku import Sudoku, INDICES


TEMPLATE = """
111111111
111111111
100000001
100111001
100111001
100111001
100000001
111111111
111111111
"""

IMPOSSIBLE_TEMPLATE = """
000000000
000000000
000000000
000111000
000111000
000111000
000000000
000000000
000000000
"""


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


class GenerateFromTemplateTests(TestCase):
    def test_same_pattern(self):
        """A sudoku generated from a template has the template's pattern."""
        template = Sudoku.decode(TEMPLATE)
        sudoku = generate_from_template(template, tries=-1)

        for row, col in product(INDICES, repeat=2):
            self.assertEqual(bool(template[row, col]), bool(sudoku[row, col]))

    def test_none_from_impossible_template(self):
        """None will be generated from an impossible template."""
        template = Sudoku.decode(IMPOSSIBLE_TEMPLATE)
        sudoku = generate_from_template(template)
        self.assertIs(sudoku, None)

    def test_none_from_zero_tries(self):
        """None will be generated from a template if we don't try."""
        template = Sudoku.decode(TEMPLATE)
        sudoku = generate_from_template(template, tries=0)
        self.assertIs(sudoku, None)

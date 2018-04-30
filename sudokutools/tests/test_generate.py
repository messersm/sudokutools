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
        """A created solution is complete and correct."""
        sudoku = create_solution()
        self.assertEqual(len(sudoku), 81)
        self.assertEqual(list(find_conflicts(sudoku)), [])


class GenerateTests(TestCase):
    def test_generated_is_solvable_and_unique(self):
        """A generated sudoku has no conflicts and is unique."""
        for i in range(10):
            sudoku = generate()
            self.assertEqual(len(list(find_conflicts(sudoku))), 0)
            self.assertEqual(is_unique(sudoku), True)

    def test_generate_min(self):
        """A generated sudoku has no less than the number of fields we want."""
        for i in range(10):
            sudoku = generate(min_count=40)
            self.assertGreaterEqual(len(sudoku), 40)


class GenerateFromTemplateTests(TestCase):
    def test_has_same_pattern(self):
        """A sudoku generated from a template has the template's pattern."""
        template = Sudoku.decode(TEMPLATE)
        sudoku = generate_from_template(template, tries=-1)

        for row, col in product(INDICES, repeat=2):
            self.assertEqual(bool(template[row, col]), bool(sudoku[row, col]))

    def test_fail_from_impossible_template(self):
        """Generating from an impossible template will fail."""
        template = Sudoku.decode(IMPOSSIBLE_TEMPLATE)
        self.assertRaises(RuntimeError, generate_from_template, template)

    def test_fail_from_zero_tries(self):
        """Generating from a template within zero tries will fail."""
        template = Sudoku.decode(TEMPLATE)
        self.assertRaises(
            RuntimeError, generate_from_template, template, tries=0)

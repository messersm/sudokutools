from unittest import TestCase

from sudokutools.analyze import is_unique, find_conflicts
from sudokutools.generate import (
    generate, generate_from_template, create_solution
)
from sudokutools.sudoku import Sudoku
from sudokutools.tests.constants import TEST_SIZES

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

TEMPLATE_16x16 = """
1111111111111111
1111111111111111
1111111111111111
1100000000000011
1100111111110011
1100111111110011
1100111111110011
1100111111110011
1100111111110011
1100111111110011
1100111111110011
1100111111110011
1100000000000011
1111111111111111
1111111111111111
1111111111111111
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
        for width, height in TEST_SIZES:
            sudoku = create_solution(size=(width, height))
            self.assertEqual(sudoku.count(), width**2 * height**2)
            self.assertEqual(list(find_conflicts(sudoku)), [])


class GenerateTests(TestCase):
    def test_generated_is_solvable_and_unique(self):
        """A generated sudoku has no conflicts and is unique."""
        for width, height in TEST_SIZES:
            count = width ** 2 * height ** 2 // 2
            sudoku = generate(min_count=count, size=(width, height))
            self.assertEqual(len(list(find_conflicts(sudoku))), 0)
            self.assertEqual(is_unique(sudoku), True)

    def test_generate_min(self):
        """A generated sudoku has no less than the number of fields we want."""
        for width, height in TEST_SIZES:
            count = width**2 * height**2 // 2
            sudoku = generate(min_count=count, size=(width, height))
            self.assertGreaterEqual(sudoku.count(), count)

    def test_generate_invalid_min(self):
        """Generating a sudoku with to many filled fields raises ValueError."""
        for width, height in TEST_SIZES:
            max_count = width**2 * height**2
            self.assertRaises(
                ValueError,
                generate, min_count=max_count+1, size=(width, height))

    def test_invalid_symmetry(self):
        """Generating a sudoku with invalid symmetry raises ValueError."""
        self.assertRaises(ValueError, generate, symmetry=2)
        self.assertRaises(ValueError, generate, symmetry="nice")


class GenerateFromTemplateTests(TestCase):
    def test_has_same_pattern(self):
        """A sudoku generated from a template has the template's pattern."""
        template = Sudoku.decode(TEMPLATE)
        sudoku = generate_from_template(template, tries=-1)

        for row, col in template:
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

    def test_different_sizes(self):
        """A 16x16 template creates a correct 16x16 sudoku."""
        # TODO: This test seems to timeout on Travis sometimes.
        template = Sudoku.decode(TEMPLATE_16x16)
        self.assertEqual(template.size, (4, 4))
        sudoku = generate_from_template(template, tries=-1)
        self.assertEqual(sudoku.size, (4, 4))

        for row, col in template:
            self.assertEqual(bool(template[row, col]), bool(sudoku[row, col]))

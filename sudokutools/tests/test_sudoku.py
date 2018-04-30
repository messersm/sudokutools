from itertools import product
from unittest import TestCase

from sudokutools.sudoku import (
    INDICES, NUMBERS, Sudoku, column_of, row_of, square_of, surrounding_of
)

EXAMPLE = """003020600
900305001
001806400
008102900
700000008
006708200
002609500
800203009
005010300"""

EXAMPLE_STR = """
    3 |   2   | 6    
9     | 3   5 |     1
    1 | 8   6 | 4    
------+-------+------
    8 | 1   2 | 9    
7     |       |     8
    6 | 7   8 | 2    
------+-------+------
    2 | 6   9 | 5    
8     | 2   3 |     9
    5 |   1   | 3    """

# Remove newline at start
EXAMPLE_STR = EXAMPLE_STR[1:]

# empty fields of the sudoku above
EMPTY = [
    (0, 0), (0, 1), (0, 3), (0, 5), (0, 7), (0, 8),
    (1, 1), (1, 2), (1, 4), (1, 6), (1, 7),
    (2, 0), (2, 1), (2, 4), (2, 7), (2, 8),
    (3, 0), (3, 1), (3, 4), (3, 7), (3, 8),
    (4, 1), (4, 2), (4, 3), (4, 4), (4, 5), (4, 6), (4, 7),
    (5, 0), (5, 1), (5, 4), (5, 7), (5, 8),
    (6, 0), (6, 1), (6, 4), (6, 7), (6, 8),
    (7, 1), (7, 2), (7, 4), (7, 6), (7, 7),
    (8, 0), (8, 1), (8, 3), (8, 5), (8, 7), (8, 8)
]

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


class SudokuTests(TestCase):
    def test_init(self):
        """A new sudoku consists of 81 zeros and no candidates.
        """
        sudoku = Sudoku()

        for row, col in product(range(9), repeat=2):
            self.assertEqual(sudoku[row, col], 0)
            self.assertEqual(sudoku.get_candidates(row, col), set())

    def test_decode(self):
        sudoku = Sudoku.decode(EXAMPLE)

        row = 0
        col = 0

        for line in EXAMPLE.split('\n'):
            for item in line:
                self.assertEqual(sudoku[row, col], int(item))
                col += 1
                if col == 9:
                    row += 1
                    col = 0

    def test_decode_candidates(self):
        sudoku = Sudoku.decode(CANDIDATES_EXAMPLE)
        self.assertEqual(sudoku.get_candidates(0, 1), {4, 5, 7, 8})

        for row, col in product(INDICES, repeat=2):
            self.assertNotEqual(sudoku.get_candidates(row, col), {})

    def test_encode(self):
        s = EXAMPLE.replace('\n', '')
        sudoku = Sudoku.decode(EXAMPLE)
        self.assertEqual(sudoku.encode(include_candidates=False), s)

    def test_str(self):
        sudoku = Sudoku.decode(EXAMPLE)
        self.assertEqual(str(sudoku), EXAMPLE_STR)

    def test_empty(self):
        """A new sudoku has 81 empty fields.
        If you set one field in this sudoku it has 80 empty fields.
        The empty() method confirms the empty fields stated in EMPTY.
        """
        sudoku = Sudoku()
        self.assertEqual(len(list(sudoku.empty())), 81)
        sudoku[0, 0] = 4
        self.assertEqual(len(list(sudoku.empty())), 80)

        sudoku = Sudoku.decode(EXAMPLE)
        self.assertEqual(list(sudoku.empty()), EMPTY)

    def test_diff(self):
        sudoku1 = Sudoku.decode(EXAMPLE)
        sudoku2 = Sudoku.decode(EXAMPLE)

        sudoku1[2, 3] -= 1
        sudoku1[4, 2] -= 1

        diff = sudoku1.diff(sudoku2)
        self.assertEqual(next(diff), (2, 3))
        self.assertEqual(next(diff), (4, 2))
        self.assertRaises(StopIteration, next, diff)

    def test_equal(self):
        """Two sudokus with the same numbers are equal.
        This is independent of their candidates.
        Changing a number in one of these sudokus makes them not-equal.
        """
        sudoku1 = Sudoku.decode(EXAMPLE)
        sudoku2 = sudoku1.copy()
        sudoku1.set_candidates(0, 0, {3, 4})

        self.assertEqual(sudoku1, sudoku2)
        sudoku1[2, 3] -= 1
        self.assertNotEqual(sudoku1, sudoku2)
        self.assertNotEqual(sudoku1, None)

    def test_equal_type(self):
        """Sudokus are equal to any object, which support [row, col]
        and return the same value on each row and column.
        Every other object simply isn't equal.
        """
        sudoku = Sudoku.decode(EXAMPLE)

        d = {}
        for row, col in product(INDICES, repeat=2):
            d[row, col] = sudoku[row, col]

        self.assertEqual(sudoku, d)
        d[0, 0] -= 1

        self.assertNotEqual(sudoku, d)
        self.assertNotEqual(sudoku, None)
        self.assertNotEqual(sudoku, 3)
        self.assertNotEqual(sudoku, {})

    def test_get_candidates(self):
        """If we get the candidates of a field
        we cannot change the returned set.
        """
        sudoku = Sudoku()
        c = sudoku.get_candidates(0, 0)
        self.assertIsInstance(c, frozenset)

    def test_set_candidates(self):
        """If we set the candidates of a field to a given set
        and change this set later on, the candidates in the field
        should not change.
        """
        sudoku = Sudoku()
        a = {3, 2, 1}
        b = set(a)
        sudoku.set_candidates(0, 0, a)
        a.discard(2)
        self.assertEqual(sudoku.get_candidates(0, 0), b)


class CoordTests(TestCase):
    def test_row_of(self):
        for row, col in product(INDICES, repeat=2):
            coords = row_of(row, col, include=True)
            self.assertEqual(len(coords), len(NUMBERS))

            for j in INDICES:
                self.assertIn((row, j), coords)

            coords = row_of(row, col, include=False)
            self.assertEqual(len(coords), len(NUMBERS)-1)
            self.assertNotIn((row, col), coords)

    def test_column_of(self):
        for row, col in product(INDICES, repeat=2):
            coords = column_of(row, col, include=True)
            self.assertEqual(len(coords), len(NUMBERS))

            for i in INDICES:
                self.assertIn((i, col), coords)

            coords = column_of(row, col, include=False)
            self.assertEqual(len(coords), len(NUMBERS)-1)
            self.assertNotIn((row, col), coords)

    def test_quad_of(self):
        for row, col in product(INDICES, repeat=2):
            coords = square_of(row, col, include=True)
            self.assertEqual(len(coords), len(NUMBERS))

            start_row = row - (row % 3)
            start_col = col - (col % 3)
            for i, j in product(range(3), repeat=2):
                self.assertIn((start_row + i, start_col + j), coords)

            coords = column_of(row, col, include=False)
            self.assertEqual(len(coords), len(NUMBERS)-1)
            self.assertNotIn((row, col), coords)

    def test_surrounding_of(self):
        for row, col in product(INDICES, repeat=2):
            coords = surrounding_of(row, col, include=True)
            self.assertEqual(len(coords), 9 + 6 + 6)

            for i, j in row_of(row, col, include=True):
                self.assertIn((i, j), coords)
            for i, j in column_of(row, col, include=True):
                self.assertIn((i, j), coords)
            for i, j in square_of(row, col, include=True):
                self.assertIn((i, j), coords)

            coords = surrounding_of(row, col, include=False)
            self.assertEqual(len(coords), 9 + 6 + 6 - 1)
            self.assertNotIn((row, col), coords)

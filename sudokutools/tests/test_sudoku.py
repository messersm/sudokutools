from itertools import product
from unittest import TestCase

from sudokutools.sudoku import Sudoku, view
from sudokutools.solve import init_candidates

EXAMPLE = """
003020600
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

EXAMPLE_4 = """
0102
2000
3004
0013
"""

EXAMPLE_4_STR = """
  1 |   2
2   |    
----+----
3   |   4
    | 1 3"""

EXAMPLE_16 = """
0 4 9 6 1 0 12 0 8 0 14 0 0 0 2 3
0 5 0 7 3 2 8 16 9 0 15 11 12 10 4 13
0 8 0 15 0 0 10 11 2 5 1 0 16 6 9 7
10 11 2 3 7 9 6 15 13 16 0 0 0 0 8 0
7 0 5 14 8 6 0 12 15 2 3 0 1 11 0 9
8 16 1 4 0 7 15 14 0 13 11 0 3 12 6 2
15 3 11 13 2 1 5 10 6 9 0 7 4 16 14 0
9 12 6 2 13 11 0 4 14 1 8 16 0 5 10 15
0 14 7 9 15 12 0 0 11 0 10 2 8 0 16 6
0 2 15 8 10 16 1 0 12 4 0 13 9 3 11 0
11 1 10 12 6 0 13 9 16 8 7 14 2 4 0 5
0 6 3 16 14 8 11 2 0 15 9 1 13 0 0 10
2 7 16 0 11 4 14 0 1 10 13 9 15 8 3 12
0 15 4 1 0 13 7 8 3 0 2 6 10 9 5 0
3 13 12 10 16 15 9 1 4 14 5 8 6 2 7 11
6 9 8 0 0 10 2 0 7 12 16 0 14 13 1 4
"""

EXAMPLE_16_STR = """
    4  9  6 |  1    12    |  8    14    |        2  3
    5     7 |  3  2  8 16 |  9    15 11 | 12 10  4 13
    8    15 |       10 11 |  2  5  1    | 16  6  9  7
10 11  2  3 |  7  9  6 15 | 13 16       |        8   
------------+-------------+-------------+------------
 7     5 14 |  8  6    12 | 15  2  3    |  1 11     9
 8 16  1  4 |     7 15 14 |    13 11    |  3 12  6  2
15  3 11 13 |  2  1  5 10 |  6  9     7 |  4 16 14   
 9 12  6  2 | 13 11     4 | 14  1  8 16 |     5 10 15
------------+-------------+-------------+------------
   14  7  9 | 15 12       | 11    10  2 |  8    16  6
    2 15  8 | 10 16  1    | 12  4    13 |  9  3 11   
11  1 10 12 |  6    13  9 | 16  8  7 14 |  2  4     5
    6  3 16 | 14  8 11  2 |    15  9  1 | 13       10
------------+-------------+-------------+------------
 2  7 16    | 11  4 14    |  1 10 13  9 | 15  8  3 12
   15  4  1 |    13  7  8 |  3     2  6 | 10  9  5   
 3 13 12 10 | 16 15  9  1 |  4 14  5  8 |  6  2  7 11
 6  9  8    |    10  2    |  7 12 16    | 14 13  1  4"""

# Remove newline at start
EXAMPLE_STR = EXAMPLE_STR[1:]
EXAMPLE_4_STR = EXAMPLE_4_STR[1:]
EXAMPLE_16_STR = EXAMPLE_16_STR[1:]

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

TEST_SIZES = ((2, 2), (2, 3), (2, 4), (3, 3), (4, 4))

SURROUNDING_OF_EXAMPLES = [
    # size, (row, col), coords
    (
        (3, 2), (1, 1),
        (
            (0, 0), (0, 1), (0, 2), (1, 0),
            (1, 1), (1, 2), (1, 3), (1, 4), (1, 5),
            (2, 1), (3, 1), (4, 1), (5, 1)
        )
     ),
]

class SudokuTests(TestCase):
    def test_init(self):
        """A new sudoku consists only of zeros and no candidates."""
        for width, height in TEST_SIZES:
            sudoku = Sudoku(size=(width, height))
            count = 0
            for row, col in sudoku:
                count += 1
                self.assertEqual(sudoku[row, col], 0)
                self.assertEqual(sudoku.get_candidates(row, col), set())
            self.assertEqual(count, width**2 * height**2, str((width, height)))

    def test_len(self):
        """A sudoku of size=(width, height) has width**2 * height**2 fields."""
        for width, height in TEST_SIZES:
            sudoku = Sudoku(size=(width, height))
            self.assertEqual(width**2 * height**2, len(sudoku))

    def test_decode_valid(self):
        """A sudoku is decoded correctly from a valid string."""
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
        """A sudoku with candidates is decoded correctly from a valid string."""
        sudoku = Sudoku.decode(CANDIDATES_EXAMPLE)
        self.assertEqual(sudoku.get_candidates(0, 1), {4, 5, 7, 8})

        for row, col in sudoku:
            self.assertNotEqual(sudoku.get_candidates(row, col), {})

    def test_decode_length_4(self):
        """A sudoku of dimensions 4x4 is decoded correctly."""
        sudoku = Sudoku.decode(EXAMPLE_4)
        self.assertEqual(str(sudoku), EXAMPLE_4_STR)
        self.assertEqual(sudoku.size, (2, 2))

    def test_decode_length_16(self):
        """A sudoku of dimensions 16x16 is decoded correctly."""
        sudoku = Sudoku.decode(EXAMPLE_16, number_sep=" ")
        self.assertEqual(str(sudoku), EXAMPLE_16_STR)
        self.assertEqual(sudoku.size, (4, 4))

    def test_encode(self):
        """A sudoku is encoded to a valid string."""
        s = EXAMPLE.replace('\n', '')
        sudoku = Sudoku.decode(EXAMPLE)
        self.assertEqual(sudoku.encode(include_candidates=False), s)

    def test_str(self):
        """str(sudoku) returns a correct human readable string."""
        sudoku = Sudoku.decode(EXAMPLE)
        self.assertEqual(str(sudoku), EXAMPLE_STR)

    def test_empty_fields_in_new_sudoku(self):
        """A new sudoku has 81 empty fields."""
        sudoku = Sudoku()
        self.assertEqual(len(list(sudoku.empty())), 81)

    def test_empty_fields_in_changed_sudoku(self):
        """If we set one field in a new sudoku it has 80 empty fields."""
        sudoku = Sudoku()
        sudoku[0, 0] = 4
        self.assertEqual(len(list(sudoku.empty())), 80)

    def test_empty_example(self):
        """empty() confirms the empty fields in a given example."""
        sudoku = Sudoku.decode(EXAMPLE)
        self.assertEqual(list(sudoku.empty()), EMPTY)

    def test_diff(self):
        """diff() confirms the differences between to given examples."""
        sudoku1 = Sudoku.decode(EXAMPLE)
        sudoku2 = Sudoku.decode(EXAMPLE)

        sudoku1[2, 3] -= 1
        sudoku1[4, 2] -= 1

        diff = sudoku1.diff(sudoku2)
        self.assertEqual(next(diff), (2, 3))
        self.assertEqual(next(diff), (4, 2))
        self.assertRaises(StopIteration, next, diff)

    def test_equal(self):
        """Two sudokus from the same string are equal."""
        sudoku1 = Sudoku.decode(EXAMPLE)
        sudoku2 = Sudoku.decode(EXAMPLE)
        self.assertEqual(sudoku1, sudoku2)

    def test_equal_independent_from_candidates(self):
        """Two sudokus are equal independent of the candidates they have."""
        sudoku1 = Sudoku.decode(EXAMPLE)
        sudoku2 = Sudoku.decode(EXAMPLE)
        sudoku1.set_candidates(0, 0, {3, 4})
        self.assertEqual(sudoku1, sudoku2)

    def test_unequal_after_change(self):
        """Changing a number in one of two equal sudokus, makes them unequal."""
        sudoku1 = Sudoku.decode(EXAMPLE)
        sudoku2 = Sudoku.decode(EXAMPLE)
        sudoku1[2, 3] -= 1
        self.assertNotEqual(sudoku1, sudoku2)

    def test_equal_type(self):
        """If an object returns the same numbers in every field, it's equal."""
        sudoku = Sudoku.decode(EXAMPLE)

        d = {}
        for row, col in sudoku:
            d[row, col] = sudoku[row, col]

        self.assertEqual(sudoku, d)

    def test_unequal_type(self):
        """If an object doesn't return the same numbers, it's unequal."""
        sudoku = Sudoku.decode(EXAMPLE)

        d = {}
        for row, col in sudoku:
            d[row, col] = sudoku[row, col]

        d[0, 0] -= 1

        self.assertNotEqual(sudoku, d)
        self.assertNotEqual(sudoku, None)
        self.assertNotEqual(sudoku, 3)
        self.assertNotEqual(sudoku, {})

    def test_candidates_are_frozenset(self):
        """The candidates of a field are a frozenset."""
        sudoku = Sudoku()
        c = sudoku.get_candidates(0, 0)
        self.assertIsInstance(c, frozenset)

    def test_cannot_change_candidates_from_outside(self):
        """The candidates of a field cannot be changed outside from Sudoku."""
        sudoku = Sudoku()
        a = {3, 2, 1}
        b = set(a)
        sudoku.set_candidates(0, 0, a)
        a.discard(2)
        self.assertEqual(sudoku.get_candidates(0, 0), b)

    def test_remove_candidates(self):
        """Removing candidates works"""
        sudoku = Sudoku()
        sudoku.set_candidates(0, 0, {1, 2, 3, 4})
        sudoku.remove_candidates(0, 0, {2, 4})
        self.assertEqual(sudoku.get_candidates(0, 0), {1, 3})

    def test_iter(self):
        """Iterating through coordinates works."""
        for width, height in (3, 3), (2, 2), (4, 2):
            sudoku = Sudoku(size=(width, height))

            coords = sorted(product(range(width * height), repeat=2))

            count = 0
            for row, col in sudoku:
                count += 1
                self.assertLess(row, width*height)
                self.assertLess(col, width*height)
                self.assertIn((row, col), coords)

            self.assertEqual(width**2 * height**2, count)


class CoordTests(TestCase):
    def test_row_of(self):
        """row_of() returns all fields of a row and no other."""
        for width, height in TEST_SIZES:
            sudoku = Sudoku(size=(width, height))

            for row, col in sudoku:
                coords = sudoku.row_of(row, col, include=True)
                self.assertEqual(len(coords), len(sudoku.numbers))

                for j in sudoku.indices:
                    self.assertIn((row, j), coords)

                coords = sudoku.row_of(row, col, include=False)
                self.assertEqual(len(coords), len(sudoku.numbers)-1)
                self.assertNotIn((row, col), coords)

    def test_column_of(self):
        """column_of() returns all fields of a column and no other."""
        for width, height in TEST_SIZES:
            sudoku = Sudoku(size=(width, height))

            for row, col in sudoku:
                coords = sudoku.column_of(row, col, include=True)
                self.assertEqual(len(coords), len(sudoku.numbers))

                for i in sudoku.indices:
                    self.assertIn((i, col), coords)

                coords = sudoku.column_of(row, col, include=False)
                self.assertEqual(len(coords), len(sudoku.numbers)-1)
                self.assertNotIn((row, col), coords)

    def test_region_of(self):
        """box_of() returns all fields of a square and no other."""
        for width, height in TEST_SIZES:
            sudoku = Sudoku(size=(width, height))

            for row, col in sudoku:
                coords = sudoku.box_of(row, col, include=True)
                self.assertEqual(len(coords), len(sudoku.numbers))

                start_row = row - (row % sudoku.height)
                start_col = col - (col % sudoku.width)
                for i in range(sudoku.height):
                    for j in range(sudoku.width):
                        self.assertIn((start_row + i, start_col + j), coords)

                coords = sudoku.box_of(row, col, include=False)
                self.assertEqual(len(coords), len(sudoku.numbers)-1)
                self.assertNotIn((row, col), coords)

    def test_surrounding_of(self):
        """surrounding_of() returns all surrounding fields and no other."""
        for width, height in TEST_SIZES:
            sudoku = Sudoku(size=(width, height))

            for row, col in sudoku:
                coords = sudoku.surrounding_of(row, col, include=True)
                count = 3 * sudoku.width * sudoku.height
                count -= (sudoku.width + sudoku.height)
                self.assertEqual(len(coords), count, str((width, height)))

                for i, j in sudoku.row_of(row, col, include=True):
                    self.assertIn((i, j), coords)
                for i, j in sudoku.column_of(row, col, include=True):
                    self.assertIn((i, j), coords)
                for i, j in sudoku.box_of(row, col, include=True):
                    self.assertIn((i, j), coords)

                coords = sudoku.surrounding_of(row, col, include=False)
                self.assertEqual(len(coords), count - 1)
                self.assertNotIn((row, col), coords)

    def test_surrounding_of_examples(self):
        """surrounding_of() returns the right coords for a given example."""
        for (width, height), (row, col), coords in SURROUNDING_OF_EXAMPLES:
            sudoku = Sudoku(size=(width, height))
            self.assertEqual(
                sorted(sudoku.surrounding_of(row, col)), sorted(coords))

    def test_box_at(self):
        """box_at() returns the correct box indices."""

        for width, height in TEST_SIZES:
            sudoku = Sudoku(size=(width, height))
            l = []
            for i in range(sudoku.width):
                for j in range(sudoku.height):
                    for x in range(sudoku.height):
                        l.extend([x + i * sudoku.height] * sudoku.width)

            boxes = [sudoku.box_at(r, c) for r, c in sudoku]
            self.assertEqual(l, boxes)


# view() tests
EXAMPLE_2x3 = """
000530
204000
150000
000205
500006
000010
"""

EXAMPLE_2x3_VIEW = """
  *46   *46 |  *126     5 |     3  *124
    2   *36 |     4  *136 |   *56    *1
    1     5 |  *236   *36 |  *246   *24
------------+-------------+------------
 *346 *1346 |  *136     2 |    *4     5
    5 *1234 |   *13  *134 |   *24     6
 *346 *2346 |  *356  *346 |     1  *234"""

EXAMPLE_9x9 = """
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

EXAMPLE_9x9_VIEW = """
45     4578   3      | 49     2      147    | 6      5789   57    
9      24678  47     | 3      47     5      | 78     278    1     
25     257    1      | 8      79     6      | 4      23579  2357  
---------------------+----------------------+---------------------
345    345    8      | 1      3456   2      | 9      34567  34567 
7      123459 49     | 459    34569  4      | 1      13456  8     
1345   13459  6      | 7      3459   8      | 2      1345   345   
---------------------+----------------------+---------------------
134    1347   2      | 6      478    9      | 5      1478   47    
8      1467   47     | 2      457    3      | 17     1467   9     
46     4679   5      | 4      1      47     | 3      24678  2467  """

EXAMPLE_16x16 = """
0 4 9 6 1 0 12 0 8 0 14 0 0 0 2 3
0 5 0 7 3 2 8 16 9 0 15 11 12 10 4 13
0 8 0 15 0 0 10 11 2 5 1 0 16 6 9 7
10 11 2 3 7 9 6 15 13 16 0 0 0 0 8 0
7 0 5 14 8 6 0 12 15 2 3 0 1 11 0 9
8 16 1 4 0 7 15 14 0 13 11 0 3 12 6 2
15 3 11 13 2 1 5 10 6 9 0 7 4 16 14 0
9 12 6 2 13 11 0 4 14 1 8 16 0 5 10 15
0 14 7 9 15 12 0 0 11 0 10 2 8 0 16 6
0 2 15 8 10 16 1 0 12 4 0 13 9 3 11 0
11 1 10 12 6 0 13 9 16 8 7 14 2 4 0 5
0 6 3 16 14 8 11 2 0 15 9 1 13 0 0 10
2 7 16 0 11 4 14 0 1 10 13 9 15 8 3 12
0 15 4 1 0 13 7 8 3 0 2 6 10 9 5 0
3 13 12 10 16 15 9 1 4 14 5 8 6 2 7 11
6 9 8 0 0 10 2 0 7 12 16 0 14 13 1 4
"""

EXAMPLE_16x16_VIEW = """
   *13,16         4         9         6 |         1        *5        12     *5,13 |         8        *7        14       *10 |     *5,11       *15         2         3
    *1,14         5       *14         7 |         3         2         8        16 |         9        *6        15        11 |        12        10         4        13
*12,13,14         8    *13,14        15 |        *4       *14        10        11 |         2         5         1   *3,4,12 |        16         6         9         7
       10        11         2         3 |         7         9         6        15 |        13        16     *4,12     *4,12 |        *5     *1,14         8     *1,14
----------------------------------------+-----------------------------------------+-----------------------------------------+----------------------------------------
        7       *10         5        14 |         8         6       *16        12 |        15         2         3     *4,10 |         1        11       *13         9
        8        16         1         4 |        *9         7        15        14 |     *5,10        13        11     *5,10 |         3        12         6         2
       15         3        11        13 |         2         1         5        10 |         6         9       *12         7 |         4        16        14        *8
        9        12         6         2 |        13        11        *3         4 |        14         1         8        16 |        *7         5        10        15
----------------------------------------+-----------------------------------------+-----------------------------------------+----------------------------------------
  *4,5,13        14         7         9 |        15        12      *3,4      *3,5 |        11        *3        10         2 |         8        *1        16         6
       *5         2        15         8 |        10        16         1      *5,7 |        12         4        *6        13 |         9         3        11       *14
       11         1        10        12 |         6        *3        13         9 |        16         8         7        14 |         2         4       *15         5
     *4,5         6         3        16 |        14         8        11         2 |        *5        15         9         1 |        13        *7       *12        10
----------------------------------------+-----------------------------------------+-----------------------------------------+----------------------------------------
        2         7        16        *5 |        11         4        14      *5,6 |         1        10        13         9 |        15         8         3        12
      *14        15         4         1 |       *12        13         7         8 |         3       *11         2         6 |        10         9         5       *16
        3        13        12        10 |        16        15         9         1 |         4        14         5         8 |         6         2         7        11
        6         9         8     *5,11 |        *5        10         2      *3,5 |         7        12        16       *15 |        14        13         1         4"""

# Remove leading newline
EXAMPLE_2x3_VIEW = EXAMPLE_2x3_VIEW[1:]
EXAMPLE_9x9_VIEW = EXAMPLE_9x9_VIEW[1:]
EXAMPLE_16x16_VIEW = EXAMPLE_16x16_VIEW[1:]


class ViewTests(TestCase):
    def test_9x9(self):
        sudoku = Sudoku.decode(EXAMPLE_9x9)
        init_candidates(sudoku)
        self.assertEqual(
            view(sudoku, candidate_prefix="", align_right=False),
            EXAMPLE_9x9_VIEW)

    def test_16x16(self):
        sudoku = Sudoku.decode(EXAMPLE_16x16, number_sep=" ")
        init_candidates(sudoku)
        self.assertEqual(view(sudoku), EXAMPLE_16x16_VIEW)

    def test_2x3(self):
        sudoku = Sudoku.decode(EXAMPLE_2x3, size=(2, 3))
        init_candidates(sudoku)
        self.assertEqual(view(sudoku), EXAMPLE_2x3_VIEW)

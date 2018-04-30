"""Parse, print and compare sudokus.

Classes defined here:
 * Sudoku: Represents a sudoku.

Functions defined here:
 * column_of(): Returns all coordinates in the column of a given field.
 * row_of(): Returns all coordinates in the row of a given field.
 * square_of(): Returns all coordinates in the square of a given field.
 * surrounding_of(): Returns all surrounding coordinates of a given field.
"""

from itertools import product
from string import whitespace

INDICES = (0, 1, 2, 3, 4, 5, 6, 7, 8)
NUMBERS = (1, 2, 3, 4, 5, 6, 7, 8, 9)


class Sudoku(object):
    """Represents a sudoku.

    This class provides methods to read, write, copy and display data to
    and from a sudoku as well as compare one sudoku with another. It stores
    9x9 fields and the numbers and candidates within these fields.

    Coordinates for row and column access are values from 0 to 8 (including).
    Using other values will most likely raise an IndexError (even though
    negative numbers are supported, they should not be used).

    Overview:

    Data access (read, write):
     * __getitem__()
     * __setitem__()
     * get_candidates()
     * set_candidates()
     * remove_candidates()

    Copying:
     * copy()

    Comparing:
     * empty()
     * __len__()
     * __eq__()
     * diff()

    Printing:
     * __str__()
     * encode()

    Parsing:
     * decode()
    """

    def __init__(self):
        self.__numbers = [[0] * 9 for _ in range(9)]
        self.__candidates = [[frozenset()] * 9 for _ in range(9)]

    def empty(self):
        """Iterate through the coordinates of all empty fields.

        Yields:
            (int, int): row and column of the next empty field.
        """
        for row, col in product(INDICES, repeat=2):
            if not self.__numbers[row][col]:
                yield row, col

    def diff(self, other):
        """Iterate through coordinates with different values in other.

        Compares each field in other to the corresponding field in
        self and yield the coordinates, if the number within is
        different.

        Args:
            other (Sudoku): Most likely another :class:`Sudoku` instance,
                            but any object, which can be accessed by
                            other[row, col] is valid.

        Yields:
            (int, int): row and column of the next different field.
        """
        for row, col in product(INDICES, repeat=2):
            if self[row, col] != other[row, col]:
                yield row, col

    def copy(self, include_candidates=False):
        """Returns a copy of this sudoku.

        Args:
            include_candidates (bool): Whether to copy candidates as well.

        Returns:
            Sudoku: The new sudoku instance.
        """
        sudoku = Sudoku()
        for row, col in product(INDICES, repeat=2):
            sudoku[row, col] = self[row, col]

        if include_candidates:
            for row, col in product(INDICES, repeat=2):
                c = self.get_candidates(row, col)
                sudoku.set_candidates(row, col, c)

        return sudoku

    def __eq__(self, other):
        """Return if other is equal in all fields.

        Args:
            other (Sudoku): Most likely another :class:`Sudoku` instance,
                            but any object, which can be accessed by
                            other[row, col] is valid.

        Returns:
            bool: True, if all fields are equal and false if not or other
                  is an incompatible type.
        """
        try:
            for row, col in product(INDICES, repeat=2):
                if self[row, col] != other[row, col]:
                    return False
            return True
        except (IndexError, KeyError, TypeError):
            return False

    def __str__(self):
        """Return sudoku as a human-readable string.

        Returns:
            str: String representing the sudoku.
        """
        s = ""

        for rc, row in enumerate(INDICES):
            col_str = []
            for cc, col in enumerate(INDICES):
                val = str(self[row, col])
                if val == "0":
                    val = " "
                col_str.append(val)
                if cc % 3 == 2 and cc < 8:
                    col_str.append("|")

            s += " ".join(col_str)

            if rc < 8:
                s += "\n"

            if rc % 3 == 2 and rc < 8:
                s += "------+-------+------\n"
        return s

    def __getitem__(self, key):
        """Return the number in the field referenced by key.

        Args:
            key (int, int): row and column of the requested field.
                            Must be in range(0, 9).

        Returns:
            int: The number in the given field, 0 representing an empty field.

        Raises:
            IndexError: if the given coordinates are not valid.
        """
        row, col = key
        return self.__numbers[row][col]

    def __setitem__(self, key, value):
        """Set the number in the field referenced by key to value.

        Args:
            key (int, int): row and column of the requested field.
                            Must be in range(0, 9).
            value (int): The number to set the field to,
                         0 representing an empty field.

        Raises:
            IndexError: if the given coordinates are not valid.
        """
        row, col = key
        self.__numbers[row][col] = value

    def __len__(self):
        """Return the number of non-empty fields in this sudoku.

        Returns:
            int: The number of non-empty fields within this sudoku.
        """
        count = 0
        for row, col in product(INDICES, repeat=2):
            if self.__numbers[row][col]:
                count += 1
        return count

    def get_candidates(self, row, col):
        """Return the candidates of the field at (row, col).

        Args:
            row (int): The row of the field.
            col (int): The column of the field.

        Returns:
            frozenset: The candidates at (row, col).
        """
        return self.__candidates[row][col]

    def set_candidates(self, row, col, value):
        """Set the candidates of the field at (row, col) to value.

        Args:
            row (int): The row of the field.
            col (int): The column of the field.
            value (iterable): The candidates to set the field to.
        """

        self.__candidates[row][col] = frozenset(value)

    def remove_candidates(self, row, col, *candidates):
        """Remove the given candidates in the field at (row, col).

        Ignores candidates, which are not present in the field.

        Args:
            row (int): The row of the field.
            col (int): The column of the field.
            candidates (iterable): The candidates to remove.
        """
        self.__candidates[row][col] -= set(candidates)

    def encode(self, row_sep="", col_sep="", include_candidates=False):
        """Return sudoku as a (machine-readable) string.

        This method is mainly provided to output sudokus in a
        machine-readable format, but can be used for creating
        nicely looking representations as well.

        Args:
            row_sep (str): Separator between rows.
            col_sep (str): Separator between columns.
            include_candidates:

        Returns:
            (str): String representing this sudoku.

        For examples of default output string see decode().
        """
        rows = []
        for row in INDICES:
            numbers = [str(self[row, col]) for col in INDICES]
            rows.append(col_sep.join(numbers))

        s = row_sep.join(rows)

        if include_candidates:
            all_candidates = []

            for row, col in product(INDICES, repeat=2):
                clist = list(self.get_candidates(row, col))
                cstr = "".join([str(i) for i in sorted(clist)])
                all_candidates.append(cstr)

            s += "|" + ",".join(all_candidates)

        return s

    @classmethod
    def decode(cls, s):
        """Create a new sudoku from the string s.

        Args:
            s (str): A string representing the sudoku (see below).

        Returns:
            Sudoku: The newly created :class:`Sudoku` instance.

        Examples for s:
            000030000005009602008004013020060000703040106000080090210300800306800700000020000
            000030000005009602008004013020060000703040106000080090210300800306800700000020000|124,235

        Whitespace is ignored while parsing the string, so you can place
        newlines for better readability.

        Each number represents the value of a column. If a row is full, we
        continue in the next one. So the sudoku above looks like this::

                  |   3   |
                5 |     9 | 6   2
                8 |     4 |   1 3
            ------+-------+------
              2   |   6   |
            7   3 |   4   | 1   6
                  |   8   |   9
            ------+-------+------
            2 1   | 3     | 8
            3   6 | 8     | 7
                  |   2   |

        The second string additionally defines candidates. Each set
        of candidates is separated by ',' so the string above defines the
        candidates for (0, 0) to be 1, 2 and 4 and for (0, 1) to be 2, 3 and 5

        This is the default format, which encode() uses and no other
        format is supported right now.
        """
        if '|' in s:
            s, c_str = s.split('|', 1)
        else:
            c_str = ""

        # read sudoku fields
        sudoku = Sudoku()
        col = 0
        row = 0

        for item in s:
            if item in whitespace:
                continue

            sudoku[row, col] = int(item)
            col += 1
            if col >= 9:
                row += 1
                col = 0
            if row >= 9:
                break

        # read candidates
        for c in whitespace:
            c_str = c_str.replace(c, '')
        c_str = c_str.split(',')

        col = 0
        row = 0

        for c in c_str:
            if c in whitespace:
                continue

            sudoku.set_candidates(row, col, set([int(item) for item in c]))
            col += 1
            if col == 9:
                col = 0
                row += 1
            if row == 9:
                break

        return sudoku


def column_of(row, col, include=True):
    """Return all coordinates in the column of (col, row) as a list.

    Args:
        row (int): The row of the field.
        col (int): The column of the field.
        include (bool): Whether or not to include (row, col).

    Returns:
        list of (int, int): list of pairs (row, column) of all fields in
                            the same column.
    """
    return [(i, col) for i in INDICES if include or i != row]


def row_of(row, col, include=True):
    """Return all coordinates in the row of (col, row) as a list.

    Args:
        row (int): The row of the field.
        col (int): The column of the field.
        include (bool): Whether or not to include (row, col).

    Returns:
        list of (int, int): list of pairs (row, column) of all fields in
                            the same row.
    """
    return [(row, j) for j in INDICES if include or j != col]


def square_of(row, col, include=True):
    """Return all coordinates in the square of (col, row) as a list.

    Args:
        row (int): The row of the field.
        col (int): The column of the field.
        include (bool): Whether or not to include (row, col).

    Returns:
        list of (int, int): list of pairs (row, column) of all fields in
                            the same square.
    """
    grid_x = col - (col % 3)
    grid_y = row - (row % 3)

    coords = [(grid_y + i, grid_x + j) for i in range(3) for j in range(3)]
    if not include:
        coords.remove((row, col))
    return coords


def surrounding_of(row, col, include=True):
    """Return all surrounding coordinates of (col, row) as a list.

    Args:
        row (int): The row of the field.
        col (int): The column of the field.
        include (bool): Whether or not to include (row, col).

    Returns:
        list of (int, int): list of pairs (row, column) of all fields in
                            the same column, row or square.
    """
    coords = row_of(row, col, include=include)
    coords.extend(column_of(row, col, include=include))
    coords.extend(_quad_without_row_and_column_of(row, col))

    # remove two items of (col, row) in coords (there are three)
    if include:
        coords.remove((row, col))

    return coords


def _quad_without_row_and_column_of(row, col):
    """Return some coordinates in the square of (col, row) as a list.

    The coordinates in the same row and column are removed.

    This is an internal function and should not be used
    outside of the sudoku module.
    """
    grid_x = col - (col % 3)
    grid_y = row - (row % 3)

    return [(grid_y + i, grid_x + j) for i, j in product(
        range(3), repeat=2) if grid_y + i != row and grid_x + j != col]

"""Parse, print and compare sudokus.

Classes defined here:
 * Sudoku: Represents a sudoku.

Functions defined here:
 * view(): Return sudoku (with candidates) as a human-readable string.
"""

from itertools import product
from string import whitespace


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

    def __init__(self, size=(3, 3)):
        """Create a new empty sudoku.

        Args:
            size ((int, int)): box_width, box_height for the new sudoku.
        """
        try:
            self.size = tuple(size)
            self.width = size[0]
            self.height = size[1]
            self.indices = tuple(range(size[0] * size[1]))
            self.numbers = tuple(range(1, size[0] * size[1] + 1))
        except (IndexError, KeyError):
            raise ValueError("Invalid sudoku size: %s" % size)
        self.__numbers = [[0] * len(self.indices) for _ in self.indices]
        self.__candidates = [[frozenset()] * len(self.indices)
                             for _ in self.indices]

    def __iter__(self):
        """Iterate through all coordinates of the sudoku.

        Yields: (int, int): row and column of each field.
        """
        for row, col in product(self.indices, repeat=2):
            yield (row, col)

    def empty(self):
        """Iterate through the coordinates of all empty fields.

        Yields:
            (int, int): row and column of the next empty field.
        """
        for row, col in self:
            if not self.__numbers[row][col]:
                yield row, col

    def filled(self):
        """Iterate through the coordinates of filled fields.

        Yields:
            (int, int): row and column of the next filled field.
        """
        for row, col in self:
            if self.__numbers[row][col]:
                yield row, col

    def count(self):
        """Return the number of filled fields.

        Returns:
            int: number of filled fields.
        """
        return len(list(self.filled()))

    def diff(self, other):
        """Iterate through coordinates with different values in other.

        Compares each field in other to the corresponding field in
        self and yields the coordinates, if the number within is
        different.

        Args:
            other (Sudoku): Most likely another :class:`Sudoku` instance,
                            but any object, which can be accessed by
                            other[row, col] is valid.

        Yields:
            (int, int): row and column of the next different field.
        """
        for row, col in self:
            if self[row, col] != other[row, col]:
                yield row, col

    def copy(self, include_candidates=False):
        """Returns a copy of this sudoku.

        Args:
            include_candidates (bool): Whether to copy candidates as well.

        Returns:
            Sudoku: The new sudoku instance.
        """
        sudoku = Sudoku(size=self.size)
        for row, col in self:
            sudoku[row, col] = self[row, col]

        if include_candidates:
            for row, col in self:
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
            for row, col in self:
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
        return view(self, include_candidates=False)

    def __getitem__(self, key):
        """Return the number in the field referenced by key.

        Args:
            key (int, int): row and column of the requested field.
                            Must be in range(0, width * height).

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
                            Must be in range(0, width * height).
            value (int): The number to set the field to,
                         0 representing an empty field.

        Raises:
            IndexError: if the given coordinates are not valid.
        """
        row, col = key
        self.__numbers[row][col] = value

    def __len__(self):
        """Return the number of fields in this sudoku.

        Returns:
            int: The number of fields in this sudoku.
        """
        return self.width ** 2 * self.height ** 2

    def get_number(self, row, col):
        """Same as sudoku[row, col]."""
        return self[row, col]

    def set_number(self, row, col, value):
        """Same as sudoku[row, col] = value."""
        self[row, col] = value

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

    def remove_candidates(self, row, col, value):
        """Remove the given candidates in the field at (row, col).

        Ignores candidates, which are not present in the field.

        Args:
            row (int): The row of the field.
            col (int): The column of the field.
            value (iterable): The candidates to remove.
        """
        self.__candidates[row][col] -= set(value)

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
        for row in self.indices:
            numbers = [str(self[row, col]) for col in self.indices]
            rows.append(col_sep.join(numbers))

        s = row_sep.join(rows)

        if include_candidates:
            all_candidates = []

            for row, col in self:
                clist = list(self.get_candidates(row, col))
                cstr = "".join([str(i) for i in sorted(clist)])
                all_candidates.append(cstr)

            s += "|" + ",".join(all_candidates)

        return s

    @classmethod
    def decode(cls, s, empty="0", number_sep=None, sudoku_sep="|", candidate_sep=",", size=None):
        """Create a new sudoku from the string s.

        Args:
            s (str): A string representing the sudoku (see below).
            empty (char): A character representing empty fields.
            sudoku_sep (char): A character, which separates field information
                               from candidate information.
            candidate_sep (char): A character separating the candidate lists.
            size (int, int): (width, height) of the new sudoku. If not given
                             This will be calculated automatically, which
                             may lead to wrong results. (It will always
                             work as intended if width == height.)

        Returns:
            Sudoku: The newly created sudoku.

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
        # remove leading and trailing whitespace
        s = s.strip()

        # remove all unused whitespace
        if number_sep is None:
            special = empty + sudoku_sep + candidate_sep
        else:
            special = empty + sudoku_sep + candidate_sep + number_sep

        for c in whitespace:
            if c not in special:
                if number_sep:
                    s = s.replace(c, number_sep)
                else:
                    s = s.replace(c, "")

        if sudoku_sep in s:
            sudoku_str, candidate_str = s.split(sudoku_sep, 1)
        else:
            sudoku_str = s
            candidate_str = ""

        # try to get size automatically:
        if size is None:
            if number_sep:
                count = len(sudoku_str.split(number_sep))
            else:
                count = len(sudoku_str)

            length = count**0.5

            if not length.is_integer():
                raise ValueError("Invalid number of fields given " +
                                 "(must be square number): %d" % count)

            length = int(length)
            width = length**0.5
            if width.is_integer():
                size = int(width), int(width)
            else:
                for i in range(2, length+1):
                    if length % i == 0:
                        width = i
                        break
                if width == length:
                    raise ValueError("Invalid row length: %d" % length)
                size = (width, length // width)

        # read sudoku fields
        sudoku = Sudoku(size=size)
        col = 0
        row = 0

        if number_sep:
            items = sudoku_str.split(number_sep)
        else:
            items = sudoku_str

        for item in items:
            if item is empty:
                sudoku[row, col] = 0
            else:
                sudoku[row, col] = int(item)

            col += 1
            if col >= sudoku.width * sudoku.height:
                row += 1
                col = 0
            if row >= sudoku.width * sudoku.height:
                break

        # read candidates if any
        if not candidate_str:
            return sudoku

        col = 0
        row = 0

        for c in candidate_str.split(candidate_sep):
            c = c.strip()
            if number_sep:
                candidates = [int(item) for item in c.split(number_sep)]
            else:
                candidates = [int(item) for item in c]
            sudoku.set_candidates(row, col, candidates)
            col += 1
            if col == sudoku.width * sudoku.height:
                col = 0
                row += 1
            if row == sudoku.width * sudoku.height:
                break

        return sudoku

    def box_at(self, row, col):
        """Return the box index of the field at (row, col)

        Args:
            row (int): The row of the field.
            col (int): The column of the field.

        Returns:
            int: The index of the box, in which the field (row, col) lies.
        """
        return col // self.width + row - (row % self.height)

    def column_of(self, row, col, include=True):
        """Return all coordinates in the column of (col, row) as a list.

        Args:
            row (int): The row of the field.
            col (int): The column of the field.
            include (bool): Whether or not to include (row, col).

        Returns:
            list of (int, int): list of pairs (row, column) of all fields in
                                the same column.
        """
        return [(i, col) for i in self.indices if include or i != row]

    def row_of(self, row, col, include=True):
        """Return all coordinates in the row of (col, row) as a list.

        Args:
            row (int): The row of the field.
            col (int): The column of the field.
            include (bool): Whether or not to include (row, col).

        Returns:
            list of (int, int): list of pairs (row, column) of all fields in
                                the same row.
        """
        return [(row, j) for j in self.indices if include or j != col]

    def box_of(self, row, col, include=True):
        """Return all coordinates in the region of (col, row) as a list.

        Args:
            row (int): The row of the field.
            col (int): The column of the field.
            include (bool): Whether or not to include (row, col).

        Returns:
            list of (int, int): list of pairs (row, column) of all fields in
                                the same box (region).
        """
        grid_x = col - (col % self.width)
        grid_y = row - (row % self.height)

        coords = [(grid_y + i, grid_x + j)
                  for i in range(self.height) for j in range(self.width)]
        if not include:
            coords.remove((row, col))
        return coords

    def surrounding_of(self, row, col, include=True):
        """Return all surrounding coordinates of (col, row) as a list.

        Args:
            row (int): The row of the field.
            col (int): The column of the field.
            include (bool): Whether or not to include (row, col).

        Returns:
            list of (int, int): list of pairs (row, column) of all fields in
                                the same column, row or square.
        """
        coords = self.row_of(row, col, include=include)
        coords.extend(self.column_of(row, col, include=include))
        coords.extend(self._quad_without_row_and_column_of(row, col))

        # remove two items of (col, row) in coords (there are three)
        if include:
            coords.remove((row, col))

        return coords

    def _quad_without_row_and_column_of(self, row, col):
        """Return some coordinates in the square of (col, row) as a list.

        The coordinates in the same row and column are removed.

        This is an internal function and should not be used
        outside of the sudoku module.
        """
        grid_x = col - (col % self.width)
        grid_y = row - (row % self.height)

        return [(grid_y + i, grid_x + j) for i, j in product(
                range(self.height), range(self.width))
                if grid_y + i != row and grid_x + j != col]


def view(
        sudoku,
        include_candidates=True, number_sep=None, candidate_prefix='*',
        align_right=True):
    """Return sudoku as a human-readable string.

    Args:
        sudoku: The sudoku to represent.
        include_candidates (bool): include candidates (or not)
        number_sep (str): separator for candidates. If set to None, this
                          set to ',', if there are numbers > 9 in the sudoku.
                          Otherwise it will be the empty string.
        candidate_prefix (str): A string preceding the candidates. This is
                                used to mark output as candidates (for example
                                to recognize naked singles).
        align_right (bool): Align field content to the right
                            (will be left-aligned, if set to False).

    Returns:
        str: String representing the sudoku.

    Example::

        >>> from sudokutools.solve import init_candidates
        >>> from sudokutools.sudoku import Sudoku, view
        >>> sudoku = Sudoku.decode('''
        ... 003020600
        ... 900305001
        ... 001806400
        ... 008102900
        ... 700000008
        ... 006708200
        ... 002609500
        ... 800203009
        ... 005010300''')
        >>> init_candidates(sudoku)
        >>> print(view(sudoku)) # doctest: +NORMALIZE_WHITESPACE
            *45   *4578       3 |     *49       2    *147 |       6   *5789     *57
              9  *24678     *47 |       3     *47       5 |     *78    *278       1
            *25    *257       1 |       8     *79       6 |       4  *23579   *2357
        ------------------------+-------------------------+------------------------
           *345    *345       8 |       1   *3456       2 |       9  *34567  *34567
              7 *123459     *49 |    *459  *34569      *4 |      *1  *13456       8
          *1345  *13459       6 |       7   *3459       8 |       2   *1345    *345
        ------------------------+-------------------------+------------------------
           *134   *1347       2 |       6    *478       9 |       5   *1478     *47
              8   *1467     *47 |       2    *457       3 |     *17   *1467       9
            *46   *4679       5 |      *4       1     *47 |       3  *24678   *2467
    """

    max_length = max([len(str(n)) for n in sudoku.numbers])
    if max_length > 1:
        number_sep = ","
    else:
        number_sep = ""

    # In case, candidates aren't calculated yet, this gives a
    # better representation.
    max_field_length = max_length

    if include_candidates:
        # get the maximum field length with candidates
        for row, col in sudoku:
            length = len(number_sep.join(
                [str(n) for n in sudoku.get_candidates(row, col)]))
            length += len(candidate_prefix)
            if length > max_field_length:
                max_field_length = length

    dash_count = sudoku.width + sudoku.width * max_field_length

    rule = "-" * dash_count + "+"
    for i in range(sudoku.height-2):
        rule += "-" * (dash_count + 1) + "+"
    rule += "-" * dash_count + "\n"

    s = ""

    field_count = sudoku.width * sudoku.height

    for rc, row in enumerate(sudoku.indices):
        col_str = []
        for cc, col in enumerate(sudoku.indices):
            if sudoku[row, col]:
                val = str(sudoku[row, col])
            elif not include_candidates:
                val = ""
            else:
                val = candidate_prefix + number_sep.join(
                    [str(x) for x in sorted(sudoku.get_candidates(row, col))])

            if align_right:
                val = val.rjust(max_field_length)
            else:
                val = val.ljust(max_field_length)

            col_str.append(val)
            if (cc + 1) % sudoku.width == 0 and cc < field_count - 1:
                col_str.append("|")

        s += " ".join(col_str)

        if rc < field_count - 1:
            s += "\n"

        if (rc + 1) % sudoku.height == 0 and rc < field_count - 1:
            s += rule
    return s

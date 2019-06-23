"""Calculate Sudoku coordinates

Functions defined here:
 * box_at():         Return the box index of a given field.
 * box_of():         Return all coordinates in the region of (col, row) as a list.
 * column_of():      Return all coordinates in the column of (col, row) as a list.
 * row_of():         Return all coordinates in the row of (col, row) as a list.
 * surrounding_of(): Return all surrounding coordinates of (col, row) as a list.
 * the_box():        Return all coordinates of the fields of the given box number.
 * the_column():     Return all coordinates of the fields of the given column number.
 * the_part():       Return all coordinates of the fields of the given part number.
 * the_row():        Return all coordinates of the fields of the given row number.

All coordinates and indices start with 0. So a standard Sudoku has these
row, column and box indices (box indices are the values of the table)::

    r/c| 0 1 2 3 4 5 6 7 8
    ---+------------------
     0 | 0 0 0 1 1 1 2 2 2
     1 | 0 0 0 1 1 1 2 2 2
     2 | 0 0 0 1 1 1 2 2 2
     3 | 3 3 3 4 4 4 5 5 5
     4 | 3 3 3 4 4 4 5 5 5
     5 | 3 3 3 4 4 4 5 5 5
     6 | 6 6 6 7 7 7 8 8 8
     7 | 6 6 6 7 7 7 8 8 8
     8 | 6 6 6 7 7 7 8 8 8


Parts of boxes are numbered in the same way as boxes are within a Sudoku.
So each box has the following parts::

    0 1 2
    3 4 5
    6 7 8


Note::

    Relevant for the calculation of coordinates is the ``width`` and ``height``
    of a sudoku box. Whenever a parameter is called ``width`` or ``height``
    the box dimensions is required. A standard sudoku has a width and height of 3x3.

"""

from itertools import product


def box_at(row, col, width=3, height=3):
    """Return the box index of the field at (row, col)

    Args:
        row (int): The row of the field.
        col (int): The column of the field.
        width (int): The width of the sudoku.
        height (int): The height of the sudoku.

    Returns:
        int: The index of the box, in which the field (row, col) lies.
    """
    return col // width + row - (row % height)


def box_of(row, col, width=3, height=3, include=True):
    """Return all coordinates in the region of (col, row) as a list.

    Args:
        row (int): The row of the field.
        col (int): The column of the field.
        width (int): The width of the sudoku.
        height (int): The height of the sudoku.
        include (bool): Whether or not to include (row, col).

    Returns:
        list of (int, int): list of pairs (row, column) of all fields in
                            the same box (region).
    """
    grid_x = col - (col % width)
    grid_y = row - (row % height)

    coords = [(grid_y + i, grid_x + j)
              for i in range(height) for j in range(width)]
    if not include:
        coords.remove((row, col))
    return coords


def column_of(row, col, width=3, height=3, include=True):
    """Return all coordinates in the column of (col, row) as a list.

    Args:
        row (int): The row of the field.
        col (int): The column of the field.
        width (int): The width of the sudoku.
        height (int): The height of the sudoku.
        include (bool): Whether or not to include (row, col).

    Returns:
        list of (int, int): list of pairs (row, column) of all fields in
                            the same column.
    """
    return [(i, col) for i in range(width * height) if include or i != row]


def row_of(row, col, width=3, height=3, include=True):
    """Return all coordinates in the row of (col, row) as a list.

    Args:
        row (int): The row of the field.
        col (int): The column of the field.
        width (int): The width of the sudoku.
        height (int): The height of the sudoku.
        include (bool): Whether or not to include (row, col).

    Returns:
        list of (int, int): list of pairs (row, column) of all fields in
                            the same row.
    """
    return [(row, j) for j in range(width * height) if include or j != col]


def surrounding_of(row, col, width=3, height=3, include=True):
    """Return all surrounding coordinates of (col, row) as a list.

    Args:
        row (int): The row of the field.
        col (int): The column of the field.
        width (int): The width of the sudoku.
        height (int): The height of the sudoku.
        include (bool): Whether or not to include (row, col).

    Returns:
        list of (int, int): list of pairs (row, column) of all fields in
                            the same column, row or square.
    """
    coords = row_of(row, col, width, height, include)
    coords.extend(column_of(row, col, width, height, include))
    coords.extend(_box_without_row_and_column_of(row, col, width, height))

    # remove two items of (col, row) in coords (there are three)
    if include:
        coords.remove((row, col))

    return coords


def _box_without_row_and_column_of(row, col, width, height):
    """Return some coordinates in the square of (col, row) as a list.

    The coordinates in the same row and column are removed.

    This is an internal function and should not be used
    outside of the coordinates module.
    """
    grid_x = col - (col % width)
    grid_y = row - (row % height)

    return [(grid_y + i, grid_x + j) for i, j in product(
            range(height), range(width))
            if grid_y + i != row and grid_x + j != col]


def the_box(box, width=3, height=3):
    """Return all coordinates of the fields of the given box number.

    Args:
        box (int): The number of the box.
        width (int): The width of the sudoku.
        height (int): The height of the sudoku.

    Returns:
        list: The coordinates of the box with the given number.

    Raises:
        ValueError: If the box number is invalid.

    Example::
        >>> the_box(0, width=3, height=3)
        [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2)]
    """
    if not 0 <= box < width * height:
        raise ValueError(
            "box must be less equal 0 and less than %d" % width * height)

    x = (box % height) * width
    y = (box // height) * height
    return [(y + i, x + j) for i in range(height) for j in range(width)]


def the_column(col, width=3, height=3):
    """Return all coordinates of the fields of the given column number.

    Args:
        column (int): The number of the column.
        width (int): The width of the sudoku.
        height (int): The height of the sudoku.

    Returns:
        list: The coordinates of the column with the given number.

    Raises:
        ValueError: If the column number is invalid.

    Example::
        >>> the_column(1, width=3, height=3)
        [(0, 1), (1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1), (8, 1)]
    """
    if not 0 <= col < width * height:
        raise ValueError(
            "col must be less equal 0 and less than %d" % width * height)
    return [(r, col) for r in range(width * height)]


def the_part(part, width=3, height=3):
    """Return all coordinates of the fields of the given part number.

    Args:
        part (int): The number of the part.
        width (int): The width of the sudoku.
        height (int): The height of the sudoku.

    Returns:
        list: The coordinates of the part with the given number.

    Raises:
        ValueError: If the part number is invalid.

    Example::
        >>> the_part(1, width=3, height=3)
        [(0, 1), (0, 4), (0, 7), (3, 1), (3, 4), (3, 7), (6, 1), (6, 4), (6, 7)]
    """
    if not 0 <= part < width * height:
        raise ValueError(
            "part must be less equal 0 and less than %d" % width * height)

    col = (part % width)
    row = (part // width)

    return [(row + i * height, col + j * width)
            for i in range(width) for j in range(height)]


def the_row(row, width=3, height=3):
    """Return all coordinates of the fields of the given row number.

    Args:
        row (int): The number of the row.
        width (int): The width of the sudoku.
        height (int): The height of the sudoku.

    Returns:
        list: The coordinates of the row with the given number.

    Raises:
        ValueError: If the row number is invalid.

    Example::
        >>> the_row(1, width=3, height=3)
        [(1, 0), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (1, 8)]
    """
    if not 0 <= row < width * height:
        raise ValueError(
            "row must be less equal 0 and less than %d" % width * height)

    return [(row, c) for c in range(width * height)]

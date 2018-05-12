"""Provides better printing functionality for sudokus.

Functions defined here:
 * view(): Return sudoku (with candidates) as a human-readable string.
"""

from itertools import product
from sudokutools.sudoku import INDICES


def view(sudoku, include_candidates=True):
    """Return sudoku as a human-readable string.

    Args:
        sudoku: The sudoku to represent.
        include_candidates (bool): include candidates (or not)

    Returns:
        str: String representing the sudoku.

    Example::

        >>> from sudokutools.printing import view
        >>> from sudokutools.solve import init_candidates
        >>> from sudokutools.sudoku import Sudoku
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
        46     4679   5      | 4      1      47     | 3      24678  2467
    """

    if not include_candidates:
        return str(sudoku)

    # get the maximum candidate count
    max_count = max([len(sudoku.get_candidates(row, col))
                     for (row, col) in product(INDICES, repeat=2)])

    # In case, candidates aren't calculated yet, this gives a
    # better representation.
    max_count = max([max_count, 1])

    rule = "-" * (3 + 3 * max_count) + "+"
    rule += "-" * (4 + 3 * max_count) + "+"
    rule += "-" * (3 + 3 * max_count) + "\n"

    s = ""

    for rc, row in enumerate(INDICES):
        col_str = []
        for cc, col in enumerate(INDICES):
            if sudoku[row, col]:
                val = str(sudoku[row, col]) + " " * (max_count-1)
            else:
                val = "".join([str(x) for x in
                               sorted(sudoku.get_candidates(row, col))])
                val += " " * (max_count - len(val))

            col_str.append(val)
            if cc % 3 == 2 and cc < 8:
                col_str.append("|")

        s += " ".join(col_str)

        if rc < 8:
            s += "\n"

        if rc % 3 == 2 and rc < 8:
            s += rule
    return s

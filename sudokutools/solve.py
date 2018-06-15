"""Low-level solving and checking of sudokus.

Functions defined here:
 * bruteforce(): Solves a sudoku using brute force.
 * calc_candidates(): Calculates candidates of a field in a sudoku.
 * init_candidates(): Sets the candidates for all fields in a sudoku.
 * find_conflicts(): Check sudoku for conflicting fields.
 * is_unique(): Check if a sudoku has exactly one solution.
"""

from itertools import product

# from sudokutools.sudoku import INDICES, NUMBERS, surrounding_of


def calc_candidates(sudoku, row, col):
    """Return a set of candidates of the sudoku at (row, col).

    Args:
        sudoku (Sudoku): The :class:`Sudoku` instance for which the
                         candidates are calculated.
        row (int): The row of the field
        col (int): The column of the field.

    Returns:
        set: A set of candidates for the field at (row, col)
    """
    if sudoku[row, col]:
        return {sudoku[row, col]}
    candidates = set(sudoku.numbers)

    for (i, j) in sudoku.surrounding_of(row, col, include=False):
        candidates.discard(sudoku[i, j])

    return candidates


def init_candidates(sudoku, filled_only=False):
    """Calculate and set all candidates in the sudoku.

    Sets all candidates in the sudoku based on the numbers
    (and nothing else) in the surrounding fields.

    Args:
        sudoku (Sudoku): The :class:`Sudoku` instance for which the
                         candidates are calculated.
        filled_only (bool): Only set candidate of already set fields.
                            E.g. a field with a value of 2, will get the
                            candidates {2}, but a field without a value
                            will get no candidates.
    """
    for row, col in sudoku:
        if not filled_only or sudoku[row, col]:
            sudoku.set_candidates(row, col, calc_candidates(sudoku, row, col))


def bruteforce(sudoku):
    """Solve the sudoku using brute force and yield solutions.

    Args:
        sudoku (Sudoku): The :class:`Sudoku` instance to solve.

    Yields:
        Sudoku: A solution of the sudoku.
    """

    solution = sudoku.copy()
    init_candidates(solution)
    for solution in _do_bruteforce(solution):
        yield solution.copy()


def _do_bruteforce(sudoku):
    """Solve sudoku _inplace_ and yield it in a solved configuration.

    This is an internal function and should not be used
    outside of the solve module.
    """

    sorted_empty = sorted(
        list(sudoku.empty()), key=lambda c: len(sudoku.get_candidates(*c)))

    try:
        row, col = sorted_empty[0]
    except IndexError:
        yield sudoku
        return

    for candidate in list(sudoku.get_candidates(row, col)):
        sudoku[row, col] = candidate

        # save a copy of the candidates in fields, which will be changed
        saved_candidates = {(row, col): set(sudoku.get_candidates(row, col))}
        for (i, j) in sudoku.surrounding_of(row, col, include=False):
            saved_candidates[(i, j)] = set(sudoku.get_candidates(i, j))
            sudoku.remove_candidates(i, j, {candidate})

        for solution in _do_bruteforce(sudoku):
            yield solution

        # revert candidate changes and continue with next candidate
        for (i, j), value in saved_candidates.items():
            sudoku.set_candidates(i, j, value)
        sudoku[row, col] = 0


def find_conflicts(sudoku, *coords):
    """Yield conflicts in sudoku at coords.

    If coords is empty all possible coordinates will be searched.

    Args:
        sudoku (Sudoku): The :class:`Sudoku` instance to check.
        coords (iterable of (int, int)): The coordinates to search within.

    Yields:
        ((int, int), (int, int), int): tuple of coordinate pairs and the
                                       offending value.
        E.g.: ((2, 3), (2, 6), 2) indicates, that there is a conflict for
        the fields (2, 3) and (2, 6) because both of them contain a 2.
    """
    if not coords:
        coords = list(sudoku)

    for row, col in coords:
        value = sudoku[row, col]
        if not value:
            continue
        else:
            for (i, j) in sudoku.surrounding_of(row, col, include=False):
                if sudoku[i, j] == value:
                    yield ((row, col), (i, j), value)


def is_unique(sudoku):
    """Check if sudoku has exactly one solution.

    Args:
        sudoku (Sudoku): The :class:`Sudoku` instance to check.

    Returns:
        bool: Whether or not the sudoku is unique.
    """
    solutions = bruteforce(sudoku)

    # If we have no solutions return False.
    try:
        next(solutions)
    except StopIteration:
        return False

    # If we have two (or more solutions return False
    # otherwise return True.
    try:
        next(solutions)
        return False
    except StopIteration:
        return True

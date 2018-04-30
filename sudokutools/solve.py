"""Low-level solving and checking of sudokus.

Functions defined here:
 * bruteforce(): Solves a sudoku using brute force.
 * calc_candidates(): Calculates candidates of a field in a sudoku.
 * init_candidates(): Sets the candidates for all fields in a sudoku.
 * find_conflicts(): Check sudoku for conflicting fields.
 * is_unique(): Check if a sudoku has exactly one solution.
"""

from itertools import product

from sudokutools.sudoku import INDICES, NUMBERS, surrounding_of


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
    candidates = set(NUMBERS)

    for (i, j) in surrounding_of(row, col, include=False):
        candidates.discard(sudoku[i, j])

    return candidates


def init_candidates(sudoku):
    """Calculate and set all candidates in the sudoku.

    Sets all candidates in the sudoku based on the numbers
    (and nothing else) in the surrounding fields.

    Args:
        sudoku (Sudoku): The :class:`Sudoku` instance for which the
                         candidates are calculated.
    """
    for row, col in product(INDICES, repeat=2):
        sudoku.set_candidates(row, col, calc_candidates(sudoku, row, col))


def bruteforce(sudoku, reverse=False):
    """Solve the sudoku using brute force and return a solution or None.

    Args:
        sudoku (Sudoku): The :class:`Sudoku` instance to solve.
        reverse: Solve the sudoku in reverse order, meaning that
                 if a field has multiple valid numbers (a, b, c)
                 use c instead of a. This only creates another solution,
                 if the sudoku is not unique.

    Returns:
        Sudoku: The solution of the sudoku.
        None: If the sudoku is not solvable.
    """

    solution = sudoku.copy()
    init_candidates(solution)
    if _do_bruteforce(solution, reverse=reverse):
        return solution
    else:
        return None


def _do_bruteforce(sudoku, reverse=False):
    """Solve sudoku _inplace_ and return the success status.

    This is an internal function and should not be used
    outside of the solve module.
    """

    sorted_empty = sorted(
        list(sudoku.empty()), key=lambda c: len(sudoku.get_candidates(*c)))

    try:
        row, col = sorted_empty[0]
    except IndexError:
        return True

    next_candidates = list(sudoku.get_candidates(row, col))

    if reverse:
        next_candidates = reversed(next_candidates)
    for candidate in next_candidates:
        sudoku[row, col] = candidate

        # save a copy of the candidates in fields, which will be changed
        saved_candidates = {(row, col): set(sudoku.get_candidates(row, col))}
        for (i, j) in surrounding_of(row, col, include=False):
            saved_candidates[(i, j)] = set(sudoku.get_candidates(i, j))
            sudoku.remove_candidates(i, j, candidate)

        if _do_bruteforce(sudoku, reverse=reverse):
            return True
        # revert candidate changes and continue with next candidate
        else:
            for key, value in saved_candidates.items():
                i, j = key
                sudoku.set_candidates(i, j, value)
            sudoku[row, col] = 0

    # If we do reach this point, no candidate was valid, thus
    # the sudoku is not solvable at this point.
    # The solution must be found higher up the call tree.
    return False


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
        coords = product(INDICES, repeat=2)

    for row, col in coords:
        value = sudoku[row, col]
        if not value:
            continue
        else:
            for (i, j) in surrounding_of(row, col, include=False):
                if sudoku[i, j] == value:
                    yield ((row, col), (i, j), value)


def is_unique(sudoku):
    """Check if sudoku has exactly one solution.

    Args:
        sudoku (Sudoku): The :class:`Sudoku` instance to check.

    Returns:
        bool: Whether or not the sudoku is unique.
    """
    solution1 = bruteforce(sudoku, reverse=False)
    if not solution1:
        return False
    solution2 = bruteforce(sudoku, reverse=True)
    return solution1 == solution2

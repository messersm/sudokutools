"""Rate and check sudokus.

Functions defined here:
 * find_conflicts(): Check sudoku for conflicting fields.
 * is_solved(): Check, if a sudoku is solved.
 * is_unique(): Check if a sudoku has exactly one solution.
 * rate(): Return an integer representation of the difficulty of a sudoku.
 * score(): Return an integer representation of the work required to solve
            a sudoku.
"""

from sudokutools.solve import dlx
from sudokutools.solvers import CalculateCandidates, \
    NakedSingle, NakedPair, NakedTriple, NakedQuad, NakedQuint, \
    HiddenSingle, HiddenPair, HiddenTriple, HiddenQuad, HiddenQuint, \
    PointingPair, PointingTriple, \
    XWing, Swordfish, Jellyfish, \
    Bruteforce, \
    solve


RATINGS = {
    CalculateCandidates: 0,
    NakedSingle: 1,
    HiddenSingle: 1,
    NakedPair: 2,
    HiddenPair: 2,
    NakedTriple: 2,
    HiddenTriple: 2,
    NakedQuad: 3,
    HiddenQuad: 3,
    NakedQuint: 3,
    HiddenQuint: 3,
    PointingPair: 4,
    PointingTriple: 4,
    XWing: 5,
    Swordfish: 6,
    Jellyfish: 7,
    Bruteforce: 10
}


def rate(sudoku):
    """Rate the difficulty of a sudoku and return 0 <= rating <= 10.

    Args:
        sudoku (Sudoku): The sudoku to rate.

    Returns:
        (int): The rating (a value inclusive between 0 and 10).

    Note:
        Only completely solved sudokus get a rating of 0.
    """
    steps = []
    solve(sudoku, steps.append)
    # max() raises a ValueError, if the list is empty.
    try:
        return max([RATINGS[step.__class__] for step in steps])
    except ValueError:
        return 0


def score(sudoku):
    """Return a score for the given sudoku.

    The score depends on the number of empty field as well as
    which solve methods must be used to solve the sudoku.

    Args:
        sudoku (Sudoku): The sudoku to score.

    Returns:
        (int): The score (a value between 0 and empty * 10,
               where empty is the number of empty fields in the sudoku).
    """
    steps = []
    solve(sudoku, steps.append)
    return sum([RATINGS[step.__class__] for step in steps])


def is_solved(sudoku):
    """Check, if the sudoku is solved.

    Args:
        sudoku (Sudoku): The :class:`Sudoku` instance to check.

    Returns:
        bool: Whether or not the sudoku is solved.
    """
    return not list(sudoku.empty()) and not list(find_conflicts(sudoku))


def is_unique(sudoku):
    """Check if sudoku has exactly one solution.

    Args:
        sudoku (Sudoku): The :class:`Sudoku` instance to check.

    Returns:
        bool: Whether or not the sudoku is unique.
    """
    solutions = dlx(sudoku)

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
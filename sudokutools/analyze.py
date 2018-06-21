
from sudokutools.solvers import (
    CalculateCandidates,
    NakedSingle, NakedPair, NakedTriple, NakedQuad, NakedQuint,
    HiddenSingle, HiddenPair, HiddenTriple, HiddenQuad, HiddenQuint,
    PointingPair, PointingTriple,
    XWing, Swordfish, Jellyfish,
    Bruteforce,
    solve
)


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
    # This raises a ValueError, if the list is empty.
    try:
        return max([RATINGS[step.__class__] for step in steps])
    except ValueError:
        return 0

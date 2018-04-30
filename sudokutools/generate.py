"""Create new sudokus.

Functions defined here:
 * create_solution(): Create a complete sudoku without conflicts.
 * generate(): Create a new sudoku.
"""

from itertools import product
from random import shuffle

from sudokutools.solve import bruteforce, is_unique
from sudokutools.sudoku import INDICES, NUMBERS, Sudoku, square_of

SYMMETRY = {
    None: lambda r, c: [(r, c)],
    "rotate-90": lambda r, c: [(r, c), (8-c, r), (8-r, 8-c), (c, 8-r)],
    "rotate-180": lambda r, c: [(r, c), (8-r, 8-c)],
    "mirror-x": lambda r, c: [(r, c), (8-r, c)],
    "mirror-y": lambda r, c: [(r, c,), (r, 8-c)],
    "mirror-xy": lambda r, c: [(r, c), (8-r, c), (r, 8-c), (8-r, 8-c)]
}


def create_solution():
    """Returns a sudoku, without empty or conflicting fields.

    Returns:
        Sudoku: The completely filled :class:`Sudoku` instance.
    """
    sudoku = Sudoku()

    cols = [0, 3, 6]
    shuffle(cols)

    c = 0
    for i in (0, 1, 2):
        row = i * 3
        col = cols[i]

        numbers = list(NUMBERS)
        shuffle(numbers)

        for row, col in square_of(row, col):
            sudoku[row, col] = numbers.pop()
            c += 1

    return bruteforce(sudoku, reverse=False)


def generate(min_count=17, symmetry=None):
    """Generate a sudoku and return it.

    Args:
        min_count (int): Number of fields that must be filled at least.
                         Any number above 81 will raise a ValueError,
                         Any number below 17 makes no sense (but will not
                         cause an error), since unique sudokus must have
                         at least 17 filled fields.
        symmetry (str): The kind of symmetry that will be created.
                        Possible values are: None (no symmetry),
                        "rotate-90", "rotate-180", "mirror-x", "mirror-y"
                        and "mirror-xy".

    Returns:
        Sudoku: The generated :class:`Sudoku` instance.

    Raises:
        ValueError, if symmetry is not a valid argument.
        ValueError, if min_count > 81.
    """
    if min_count > 81:
        raise ValueError("min_count must be <= 81 (%d was given)." % min_count)

    solution = create_solution()
    sudoku = solution.copy()
    coords = [(row, col) for row, col in product(INDICES, repeat=2)]
    shuffle(coords)
    count = 81

    try:
        symmetry_func = SYMMETRY[symmetry]
    except KeyError:
        values = ", ".join([str(key) for key in SYMMETRY])
        raise ValueError("symmetry must be one of %s" % values)

    while coords:
        # get next coordinates to change
        step_coords = set(symmetry_func(*coords[0]))

        for row, col in step_coords:
            coords.remove((row, col))

        # break, if this change would set count below min_count
        if count - len(step_coords) < min_count:
            break

        # execute change
        for row, col in step_coords:
            sudoku[row, col] = 0
            count -= 1

        # test, if the change made the sudoku non-unique and revert in this case
        if not is_unique(sudoku):
            for row, col in step_coords:
                sudoku[row, col] = solution[row, col]
                count += 1

    return sudoku

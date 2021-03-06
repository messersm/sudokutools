"""Create new sudokus.

Functions defined here:
 * create_solution(): Create a complete sudoku without conflicts.
 * generate(): Create a new sudoku.
 * generate_from_template(): Create a new sudoku given a template pattern.

Warning:
    Since the functions in this module work using recursion,
    generating very large Sudokus will likely
    To be more precise: Python will raise an RecursionError,
    if ``box_width * box_height >= sys.getrecursionlimit()``.

    If you really want to generate Sudokus of this size using sudokutools,
    you have to increase the recursion limit of Python. See:
    https://stackoverflow.com/questions/3323001/what-is-the-maximum-recursion-depth-in-python-and-how-to-increase-it
"""

from collections import defaultdict
from random import choice, sample, shuffle

from sudokutools.analyze import is_unique
from sudokutools.solve import dlx
from sudokutools.sudoku import Sudoku

SYMMETRY = {
    None: lambda w, h, r, c: [(r, c)],
    "rotate-90": lambda w, h, r, c: [(r, c), (w*h-1-c, r), (w*h-1-r, w*h-1-c), (c, w*h-1-r)],
    "rotate-180": lambda w, h, r, c: [(r, c), (w*h-1-r, w*h-1-c)],
    "mirror-x": lambda w, h, r, c: [(r, c), (w*h-1-r, c)],
    "mirror-y": lambda w, h, r, c: [(r, c,), (r, w*h-1-c)],
    "mirror-xy": lambda w, h, r, c: [(r, c), (w*h-1-r, c), (r, w*h-1-c), (w*h-1-r, w*h-1-c)]
}


def create_solution(box_size=(3, 3)):
    """Returns a sudoku, without empty or conflicting fields.
    
    Args:
        box_size (int, int): box width and box height of the filled sudoku.
                             A standard 9x9 sudoku has box_size=(3, 3).

    Returns:
        Sudoku: The completely filled Sudoku instance.
    """
    sudoku = Sudoku(box_size=box_size)

    # fill a single box and let dlx do the rest
    row = choice(range(sudoku.box_height))
    col = choice(range(sudoku.box_width))
    numbers = list(sudoku.numbers)
    shuffle(numbers)

    for i, j in sudoku.box_of(row, col, include=True):
        sudoku[i, j] = numbers.pop()

    return next(dlx(sudoku))


def generate(min_count=0, symmetry=None, box_size=(3, 3)):
    """Generate a sudoku and return it.

    Args:
        min_count (int): Number of fields that must be filled at least.
                         Any number above 81 will raise a ValueError,
                         Any number below 17 makes no sense (but will not
                         cause an error), since unique sudokus must have
                         at least 17 filled fields.
        symmetry (str):  The kind of symmetry that will be created.
                         Possible values are: None (no symmetry),
                         "rotate-90", "rotate-180", "mirror-x", "mirror-y"
                         and "mirror-xy".
        box_size (int, int): box_width and box_height of the filled sudoku.
                         A standard 9x9 sudoku has box_size=(3, 3).

    Returns:
        Sudoku: The generated :class:`Sudoku` instance.

    Raises:
        ValueError, if symmetry is not a valid argument.
        ValueError, if min_count is larger then len(sudoku).
    """
    count_limit = box_size[0] ** 2 * box_size[1] ** 2
    if min_count > count_limit:
        raise ValueError("min_count must be <= %d (%d was given)." % (
            count_limit, min_count))

    try:
        symmetry_func = SYMMETRY[symmetry]
    except KeyError:
        values = ", ".join([str(key) for key in SYMMETRY])
        raise ValueError("symmetry must be one of %s" % values)

    solution = create_solution(box_size=box_size)
    sudoku = solution.copy()
    coords = list(sudoku)
    shuffle(coords)
    count = len(sudoku)

    while coords:
        # get next coordinates to change
        step_coords = set(symmetry_func(sudoku.box_width, sudoku.box_height, *coords[0]))

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


def generate_from_template(template, tries=100):
    """Create a new sudoku from a given template.

    Args:
        template (Sudoku): A sudoku, which describes the pattern to use.
                           Every non-zero value of the template will be
                           a filled field in the created solution.
        tries (int): The number of tries until we give up. If
                     tries < 0, the function will run, until a solution is
                     found. Take note, that this may deadlock your program,
                     if a solution is not possible.

    Returns:
        Sudoku: The created sudoku.

    Raises:
        RuntimeError: if the sudoku couldn't be created, within the
                      given number of tries.

    So symmetry isn't enough for you and you want your sudokus
    to look like your favorite animal? Then this function is for you!
    generate_from_template takes the pattern from template and returns
    a valid sudoku, which matches this pattern (if possible).

    Creating sudokus from templates is done in two steps:
     1. Create a template (Sudoku) from the template string.
     2. Hand over this template to this function.

    Example for a template string::

        111111111
        100000001
        100000001
        100111001
        100111001
        100111001
        100000001
        100000001
        111111111

    Will create a sudoku like this::

        1 2 6 | 9 4 8 | 3 7 5
        7     |       |     4
        3     |       |     6
        ------+-------+------
        9     | 8 1 2 |     3
        5     | 3 9 6 |     1
        2     | 4 5 7 |     8
        ------+-------+------
        4     |       |     7
        8     |       |     2
        6 3 7 | 1 2 5 | 4 8 9
    """
    t = 0

    while t < tries or tries < 0:
        solution = create_solution(box_size=template.box_size)
        sudoku = solution.copy()

        for row, col in template:
            if not template[row, col]:
                sudoku[row, col] = 0

        if is_unique(sudoku):
            return sudoku
        else:
            t += 1

    raise RuntimeError(
        "Failed to generate sudoku from template within %d tries." % tries)

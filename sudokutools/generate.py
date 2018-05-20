"""Create new sudokus.

Functions defined here:
 * create_solution(): Create a complete sudoku without conflicts.
 * generate(): Create a new sudoku.
 * generate_from_template(): Create a new sudoku given a template pattern.
"""

from random import sample, shuffle

from sudokutools.solve import bruteforce, is_unique
from sudokutools.sudoku import Sudoku

SYMMETRY = {
    None: lambda w, h, r, c: [(r, c)],
    "rotate-90": lambda w, h, r, c: [(r, c), (w*h-1-c, r), (w*h-1-r, w*h-1-c), (c, w*h-1-r)],
    "rotate-180": lambda w, h, r, c: [(r, c), (w*h-1-r, w*h-1-c)],
    "mirror-x": lambda w, h, r, c: [(r, c), (w*h-1-r, c)],
    "mirror-y": lambda w, h, r, c: [(r, c,), (r, w*h-1-c)],
    "mirror-xy": lambda w, h, r, c: [(r, c), (w*h-1-r, c), (r, w*h-1-c), (w*h-1-r, w*h-1-c)]
}


def create_solution(size=(3, 3)):
    """Returns a sudoku, without empty or conflicting fields.
    
    Args:
        size (int, int): region_width and region_height of the filled sudoku.

    Returns:
        Sudoku: The completely filled Sudoku instance.
    """
    sudoku = Sudoku(size=size)

    # Create a list of numbers and shuffle them.
    numbers = list(sudoku.numbers)
    shuffle(numbers)

    columns = sample(range(sudoku.width * sudoku.height), sudoku.width)

    offset = 0
    for col in columns:
        for i, j in sudoku.column_of(0, col):
            sudoku[i, j] = numbers[(offset + i) % len(numbers)]
        offset += sudoku.height

    try:
        return next(bruteforce(sudoku))
    except StopIteration:
        print("No solution found for:")
        print(sudoku)
        raise


def generate(min_count=0, symmetry=None, size=(3, 3)):
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
        size (int, int): region_width and region_height of the filled sudoku.

    Returns:
        Sudoku: The generated :class:`Sudoku` instance.

    Raises:
        ValueError, if symmetry is not a valid argument.
        ValueError, if min_count is larger then len(sudoku).
    """
    count_limit = size[0]**2 * size[1]**2
    if min_count > count_limit:
        raise ValueError("min_count must be <= %d (%d was given)." % (
            count_limit, min_count))

    solution = create_solution(size=size)
    sudoku = solution.copy()
    coords = list(sudoku)
    shuffle(coords)
    count = len(sudoku)

    try:
        symmetry_func = SYMMETRY[symmetry]
    except KeyError:
        values = ", ".join([str(key) for key in SYMMETRY])
        raise ValueError("symmetry must be one of %s" % values)

    while coords:
        # get next coordinates to change
        step_coords = set(symmetry_func(sudoku.width, sudoku.height, *coords[0]))

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
        solution = create_solution(size=template.size)
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

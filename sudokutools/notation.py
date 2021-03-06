"""Describe Sudoku coordinates using rncn and bnpn notation.

Functions defined here:
 * encode(): Converts a set of coordinates to a string.
 * decode(): Converts a string to a tuple of coordinates.

rncn notation for a standard sudoku looks like this::

    +--------------+--------------+--------------+
    |r1c1 r1c2 r1c3|r1c4 r1c5 r1c6|r1c7 r1c8 r1c9|
    |r2c1 r2c2 r2c3|r2c4 r2c5 r2c6|r2c7 r2c8 r2c9|
    |r3c1 r3c2 r3c3|r3c4 r3c5 r3c6|r3c7 r3c8 r3c9|
    +--------------+--------------+--------------+
    |r4c1 r4c2 r4c3|r4c4 r4c5 r4c6|r4c7 r4c8 r4c9|
    |r5c1 r5c2 r5c3|r5c4 r5c5 r5c6|r5c7 r5c8 r5c9|
    |r6c1 r6c2 r6c3|r6c4 r6c5 r6c6|r6c7 r6c8 r6c9|
    +--------------+--------------+--------------+
    |r7c1 r7c2 r7c3|r7c4 r7c5 r7c6|r7c7 r7c8 r7c9|
    |r8c1 r8c2 r8c3|r8c4 r8c5 r8c6|r8c7 r8c8 r8c9|
    |r9c1 r9c2 r9c3|r9c4 r9c5 r9c6|r9c7 r9c8 r9c9|
    +--------------+--------------+--------------+

Additional to row and column notation, ``encode()`` with ``allow_boxes``
set to ``True`` (which is the default) and ``decode()`` allow
the use of bnpn notation to specify coordinates.
With this notation a standard Sudoku looks like this::

    +--------------+--------------+--------------+
    |b1p1 b1p2 b1p3|b2p1 b2p2 b2p3|b3p1 b3p2 b3p3|
    |b1p4 b1p5 b1p6|b2p4 b2p5 b2p6|b3p4 b3p5 b3p6|
    |b1p7 b1p8 b1p9|b2p7 b2p8 b2p9|b3p7 b3p8 b3p9|
    +--------------+--------------+--------------+
    |b4p1 b4p2 b4p3|b5p1 b5p2 b5p3|b6p1 b6p2 b6p3|
    |b4p4 b4p5 b4p6|b5p4 b5p5 b5p6|b6p4 b6p5 b6p6|
    |b4p7 b4p8 b4p9|b5p7 b5p8 b5p9|b6p7 b6p8 b6p9|
    +--------------+--------------+--------------+
    |b7p1 b7p2 b7p3|b8p1 b8p2 b8p3|b9p1 b9p2 b9p3|
    |b7p4 b7p5 b7p6|b8p4 b8p5 b8p6|b9p4 b9p5 b9p6|
    |b7p7 b7p8 b7p9|b8p7 b8p8 b8p9|b9p7 b9p8 b9p9|
    +--------------+--------------+--------------+

For a Sudoku with 4x2 boxes it looks like this::

    +-------------------+-------------------+
    |r1c1 r1c2 r1c3 r1c4|r1c5 r1c6 r1c7 r1c8|
    |r2c1 r2c2 r2c3 r2c4|r2c5 r2c6 r2c7 r2c8|
    +-------------------+-------------------+
    |r3c1 r3c2 r3c3 r3c4|r3c5 r3c6 r3c7 r3c8|
    |r4c1 r4c2 r4c3 r4c4|r4c5 r4c6 r4c7 r4c8|
    +-------------------+-------------------+
    |r5c1 r5c2 r5c3 r5c4|r5c5 r5c6 r5c7 r5c8|
    |r6c1 r6c2 r6c3 r6c4|r6c5 r6c6 r6c7 r6c8|
    +-------------------+-------------------+
    |r7c1 r7c2 r7c3 r7c4|r7c5 r7c6 r7c7 r7c8|
    |r8c1 r8c2 r8c3 r8c4|r8c5 r8c6 r8c7 r8c8|
    +-------------------+-------------------+

    +-------------------+-------------------+
    |b1p1 b1p2 b1p3 b1p4|b2p1 b2p2 b2p3 b2p4|
    |b1p5 b1p6 b1p7 b1p8|b2p5 b2p6 b2p7 b2p8|
    +-------------------+-------------------+
    |b3p1 b3p2 b3p3 b3p4|b4p1 b4p2 b4p3 b4p4|
    |b3p5 b3p6 b3p7 b3p8|b4p5 b4p6 b4p7 b4p8|
    +-------------------+-------------------+
    |b5p1 b5p2 b5p3 b5p4|b6p1 b6p2 b6p3 b6p4|
    |b5p5 b5p6 b5p7 b5p8|b6p5 b6p6 b6p7 b6p8|
    +-------------------+-------------------+
    |b7p1 b7p2 b7p3 b7p4|b8p1 b8p2 b8p3 b8p4|
    |b7p5 b7p6 b7p7 b7p8|b8p5 b8p6 b8p7 b8p8|
    +-------------------+-------------------+

Any combination of these techniques is permitted. So "b1r1" refers
to the fields r1c1, r1c2, r1c3 where as "r1p2" refers to r1c2, r1c5 and r1c8
in a standard Sudoku and "b1" refers to all fields in the first box.

If the number of rows, columns or boxes is greater than 9, numbers
must be separated with a separation character, which defaults to ",".
For example the string "r1c1,12" describes r1c1 and r1c12.
"""

import string

from collections import defaultdict

from sudokutools.actions import RemoveCandidates, SetNumber
from sudokutools.coordinates import the_row, the_column, the_box, the_part


def encode(coordinates, width=3, height=3, use_boxes=None, sep=",", nsep=""):
    """Encode the given coordinates to a string.

    Args:
        *coordinates (iterable): The coordinates, which are to be encoded.
        width (number): The width of a box of the sudoku.
        height (number): The height of a box of the sudoku.
        use_boxes (bool or None): Whether or not to use bnpn notation.
                                   * None: Use bnpn if the result is shorter.
                                   * False: Don't use bnpn.
                                   * True: Do use bnpn.
        sep (str): A string used to separate groups of coordinates.
        nsep (str): A string used to separate numbers > 9. Will be replaced
                    by "," if it is empty and separating numbers is required.

    Returns:
        str: A string representing the given coordinates.

    Raises:
        ValueError: If there are invalid coordinates present.
        ValueError: If width or height are less than 1.
        ValueError: If width or height aren't round integers.
    """
    if int(width) != width or int(height) != height:
        raise ValueError("width and height must be round integers.")
    elif width < 1 or height < 1:
        raise ValueError("width and height must be >= 1.")

    length = width * height

    if not nsep:
        if length > 9:
            nsep = ","
        else:
            nsep = ""

    rows = defaultdict(lambda: set())
    boxes = defaultdict(lambda: set())

    for (row, col) in coordinates:
        if not 0 <= row < length or not 0 <= col < length:
            raise ValueError(
                "Invalid coordinates (%d, %d) for width = %d, height = %d." % (
                    row, col, width, height))

        box = col // width + row - (row % height)
        part = (col % width) + (row % height) * width

        rows[row].add(col)
        boxes[box].add(part)

    if use_boxes is None:
        box_str = _dict_to_str("b%sp%s", _join_keys(boxes), str(sep), str(nsep))
        row_str = _dict_to_str("r%sc%s", _join_keys(rows), str(sep), str(nsep))

        if len(box_str) < len(row_str):
            return box_str
        else:
            return row_str
    elif use_boxes:
        return _dict_to_str("b%sp%s", _join_keys(boxes), sep, nsep)
    else:
        return _dict_to_str("r%sc%s", _join_keys(rows), sep, nsep)


def decode(s, width=3, height=3, sep=",", nsep=""):
    """Decode a string into a tuple of coordinates.

    Args:
        s (str): Coordinates in rncn and bnpn notation.

    Returns:
        A tuple of coordinates described by the string s.

    Note::
        decode() will handle the same separator for groups and
        numbers just fine, because this is decided by the following
        character.
    """
    if int(width) != width or int(height) != height:
        raise ValueError("width and height must be round integers.")
    elif width < 1 or height < 1:
        raise ValueError("width and height must be >= 1.")

    length = width * height

    if not nsep:
        if length > 9:
            nsep = ","
        else:
            nsep = ""

    # remove whitespace from the string if
    # there is none present in the separators.
    if not any([c in sep for c in string.whitespace]) and \
       not any([c in nsep for c in string.whitespace]):
        s = s.replace(string.whitespace, "")

    # Split multiple groups.
    groups = [s]
    for c in "rcbp":
        new_groups = []

        for group in groups:
            for i, g in enumerate(group.split(sep + c)):
                if i > 0:
                    new_groups.append(c + g)
                else:
                    new_groups.append(g)
        groups = new_groups

    coordinates = set()
    for group in groups:
        coordinates.update(
            _decode_single(group, width=width, height=height, nsep=nsep))

    return tuple(sorted(coordinates))


def _decode_single(group, width=3, height=3, nsep=""):
    """Decode a single group string into a set of coordinates."""

    all_numbers = {
        'r': [],
        'c': [],
        'b': [],
        'p': [],
    }

    all_funcs = {
        'r': the_row,
        'c': the_column,
        'b': the_box,
        'p': the_part
    }

    current = ""        # The current item (r, c, b or p)
    present = ""        # A string containing all qualifiers already parsed.
    number_str = ""     # An accumulation of all numbers for the current item.

    for c in group:
        if c in present:
            raise ValueError(
                "Malformed group '%s'. '%s' has multiple occurrences." %
                (group, c))

        if c in all_numbers:
            if current:
                if not nsep:
                    numbers = [int(n)-1 for n in number_str]
                else:
                    numbers = [int(n)-1 for n in number_str.split(nsep)]

                if not numbers:
                    raise ValueError(
                        "Malformed group '%s'. No numbers given for '%s'" %
                        (group, current))

                all_numbers[current] = numbers

            present += current
            number_str = ""
            current = c

        elif c in string.digits or c in nsep:
            if not current:
                raise ValueError(
                    "Malformed group '%s'. '%s' is illegal at this position." %
                    (group, c))
            number_str += c

        else:
            raise ValueError(
                "Malformed group '%s'. Illegal character '%s'." %
                (group, c))

    if current:
        if not nsep:
            numbers = [int(n) - 1 for n in number_str]
        else:
            numbers = [int(n) - 1 for n in number_str.split(nsep)]

        all_numbers[current] = numbers
    elif not present:
        raise ValueError("Empty group '%s'" % group)

    all_sets = defaultdict(lambda: set())
    for key, numbers in all_numbers.items():
        # A set will only be added, if the
        # list in all_numbers is not empty.
        for number in numbers:
            all_sets[key].update(
                all_funcs[key](number, width=width, height=height))

    return set.intersection(*all_sets.values())


def encode_action(action, width=3, height=3):
    if isinstance(action, SetNumber):
        s = encode(action.coordinates, width=width, height=height)
        s += "=" + action.number
        return s
    elif isinstance(action, RemoveCandidates):
        s = encode(action.coordinates, width=width, height=height)
        s += "<>" + "".join(sorted(action.candidates))


def decode_action(s, width=3, height=3):
    s = s.strip()
    if s.startswith("-"):
        left, sep, right = s.partition(" ")
        coordinates = decode(right, width=width, height=height)
        candidates = [int(c) for c in left]
        return RemoveCandidates(coordinates, candidates)
    elif "<>" in s:
        left, sep, right = s.partition("<>")
        candidates = [int(c) for c in right]
        coordinates = decode(left, width=width, height=height)
        return RemoveCandidates(coordinates, candidates)
    elif "=" in s:
        left, sep, right = s.partition("=")
        number = int(right)
        coordinates = decode(left, width=width, height=height)
        return SetNumber(coordinates, number)
    else:
        raise ValueError("Cannot decode action '%s'" % s)


def _join_keys(a_dict):
    new_dict = {}
    for key, value in a_dict.items():
        to_add = None
        to_remove = None

        for keys, other_value in new_dict.items():
            if other_value == value:
                l = [key]
                l.extend(keys)
                l.sort()
                to_add = tuple(l)
                to_remove = keys
                break

        if to_add:
            new_dict.pop(to_remove)
            new_dict[to_add] = value
        else:
            new_dict[(key, )] = value

    return new_dict


def _dict_to_str(format_str, a_dict, sep, nsep):
    s = []

    for keys in sorted(a_dict):
        value = a_dict[keys]
        keys_str = nsep.join([str(k + 1) for k in sorted(keys)])
        value_str = nsep.join([str(v + 1) for v in sorted(value)])
        s.append(format_str % (keys_str, value_str))

    return sep.join(s)

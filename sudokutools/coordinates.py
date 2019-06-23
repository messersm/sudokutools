def the_row(row, width=3, height=3):
    """Return all coordinates of the given row."""
    if not 0 <= row < width * height:
        raise ValueError(
            "row must be less equal 0 and less than %d" % width * height)

    return tuple(
        [(row, c) for c in range(width * height)])


def the_column(col, width=3, height=3):
    """Return all coordinates of the given column."""
    if not 0 <= col < width * height:
        raise ValueError(
            "col must be less equal 0 and less than %d" % width * height)

    return tuple(
        [(r, col) for r in range(width * height)])


def the_box(box, width=3, height=3):
    """Return all coordinates of the given box."""
    if not 0 <= box < width * height:
        raise ValueError(
            "box must be less equal 0 and less than %d" % width * height)

    x = (box % height) * width
    y = (box // height) * height
    return tuple(
        [(y + i, x + j) for i in range(height) for j in range(width)])


def the_part(part, width=3, height=3):
    """Return the coordinates of the given part in all boxes"""
    if not 0 <= part < width * height:
        raise ValueError(
            "part must be less equal 0 and less than %d" % width * height)

    x = (part % width)
    y = (part // width)

    return tuple(
        [(y + i * height, x + j * width) for i in range(width) for j in range(height)])

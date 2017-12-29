def row(r, c, include=True):
    return [(r, j) for j in range(9) if include or j != c]


def col(r, c, include=True):
    return [(i, c) for i in range(9) if include or i != r]


def quad(r, c, include=True):
    grid_c = c - (c % 3)
    grid_r = r - (r % 3)

    coords = [(grid_r + i, grid_c + j) for i in range(3) for j in range(3)]
    if not include:
        coords.remove((r, c))
    return coords


def surrounding(r, c, include=True):
    coords = col(r, c, include=include)
    coords.extend(row(r, c, include=include))
    coords.extend(quad(r, c, include=include))

    # remove two items of (x, y) in coords (there are three)
    if include:
        coords.remove((r, c))
        coords.remove((r, c))
    return coords
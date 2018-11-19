"""An efficient Sudoku solver using Algorithm X with dancing links.

This is an internal module, which is kept separate from the solve
module. It is used by the sudokutools.solve.dlx() function.

None of the functions provided here should be used directly!

The original code was written by Ali Assaf and has
been slightly adapted to be used with the sudokutools library.
Written permission to use it under the MIT-License has been
granted by Ali Assaf (thank you!).

Information about the original work:
 * URL: https://www.cs.mcgill.ca/~aassaf9/python/sudoku.txt
 * Author: Ali Assaf <ali.assaf.mail@gmail.com>
 * Copyright: (C) 2010 Ali Assaf
 * License: GNU General Public License <http://www.gnu.org/licenses/>
"""

from itertools import product


def do_dlx(sudoku):
    """ An efficient Sudoku solver using Algorithm X (works _in_place_)."""
    R, C = sudoku.height, sudoku.width
    N = R * C
    X = ([("rc", rc) for rc in product(range(N), range(N))] +
         [("rn", rn) for rn in product(range(N), range(1, N + 1))] +
         [("cn", cn) for cn in product(range(N), range(1, N + 1))] +
         [("bn", bn) for bn in product(range(N), range(1, N + 1))])

    Y = dict()
    for r, c, n in product(range(N), range(N), range(1, N + 1)):
        b = (r // R) * R + (c // C) # Box number
        Y[(r, c, n)] = [
            ("rc", (r, c)),
            ("rn", (r, n)),
            ("cn", (c, n)),
            ("bn", (b, n))]

    X, Y = exact_cover(X, Y)
    for row, col in sudoku:
        n = sudoku[row, col]
        if n:
            # if this raises a KeyError, the sudoku has conflicts.
            try:
                select(X, Y, (row, col, n))
            except KeyError:
                return

    for solution in solve(X, Y, []):
        for (r, c, n) in solution:
            sudoku[r, c] = n
        yield sudoku


def exact_cover(X, Y):
    X = {j: set() for j in X}
    for i, row in Y.items():
        for j in row:
            X[j].add(i)
    return X, Y


def solve(X, Y, solution):
    if not X:
        yield list(solution)
    else:
        c = min(X, key=lambda c: len(X[c]))
        for r in list(X[c]):
            solution.append(r)
            cols = select(X, Y, r)
            for s in solve(X, Y, solution):
                yield s
            deselect(X, Y, r, cols)
            solution.pop()


def select(X, Y, r):
    cols = []
    for j in Y[r]:
        for i in X[j]:
            for k in Y[i]:
                if k != j:
                    X[k].remove(i)
        cols.append(X.pop(j))
    return cols


def deselect(X, Y, r, cols):
    for j in reversed(Y[r]):
        X[j] = cols.pop()
        for i in X[j]:
            for k in Y[i]:
                if k != j:
                    X[k].add(i)

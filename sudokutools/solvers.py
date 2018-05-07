"""High level solving of sudokus.

This module provides classes which represent typical sudoku solving
steps used by humans. Steps can be found and applied to a given
sudoku. But steps can also be printed without applying them, e.g. to inform
a user, what steps can be taken to solve the sudoku.

A single solve step may consist of multiple actions, e.g.
 * Setting a number at a given field.
 * Setting the candidates at a given field.
 * Removing some of the candidates at a given field.

Solve steps defined here:
 * NakedSingle
 * NakedPair
 * NakedTriple
 * NakedQuad
 * NakedQuint
 * HiddenSingle
 * Bruteforce
"""

from collections import namedtuple
from functools import total_ordering
from itertools import combinations

from sudokutools.solve import bruteforce
from sudokutools.sudoku import column_of, row_of, square_of, surrounding_of, \
    NUMBERS, Sudoku


class Action(namedtuple("ActionTuple", ["func", "row", "col", "value"])):
    """Named tuple, that represents a single change operation on a sudoku.

    Create with: Action(func, row, col, value)

    Args:
        func (callable): One of Sudoku.set_number, Sudoku.set_candidates and
                         Sudoku.remove_candidates
        row (int): The row of the field, which will be changed.
        col (int): The column of the field, which will be changed.
        value (int or iterable): The number or candidates to set/remove.
    """


class SolveStep(object):
    def __init__(self, *actions):
        self.__actions_build = False
        self.actions = list(actions)

    def build_actions(self, sudoku):
        self.__actions_build = True

    def apply(self, sudoku):
        if not self.__actions_build:
            self.build_actions(sudoku)

        for action in self.actions:
            action.func(sudoku, action.row, action.col, action.value)


@total_ordering
class SingleFieldStep(SolveStep):
    def __init__(self, row, col, value):
        super(SingleFieldStep, self).__init__()
        self.row = row
        self.col = col
        self.value = value

    def __eq__(self, other):
        return (self.row, self.col, self.value) == (
            other.row, other.col, other.value)

    def __lt__(self, other):
        return (self.row, self.col, self.value) < (
            other.row, other.col, other.value)

    def __str__(self):
        return "%s at (%d, %d): %d" % (
            self.__class__.__name__, self.row, self.col, self.value)

    def __repr__(self):
        return "%s(%d, %d, %d)" % (
            self.__class__.__name__, self.row, self.col, self.value)

    def build_actions(self, sudoku):
        super(SingleFieldStep, self).build_actions(sudoku)

        self.actions.append(
            Action(Sudoku.set_number, self.row, self.col, self.value))
        self.actions.append(
            Action(Sudoku.set_candidates, self.row, self.col, self.value))

        for i, j in surrounding_of(self.row, self.col, include=False):
            if self.value in sudoku.get_candidates(i, j):
                self.actions.append(
                    Action(Sudoku.remove_candidates, i, j, {self.value}))


class NakedSingle(SingleFieldStep):
    def __str__(self):
        return "Naked single at (%d, %d): %d" % (self.row, self.col, self.value)

    @classmethod
    def find(cls, sudoku):
        for row, col in sudoku.empty():
            candidates = sudoku.get_candidates(row, col)
            if len(candidates) == 1:
                for value in candidates:
                    break
                yield cls(row, col, value)


class HiddenSingle(SingleFieldStep):
    @classmethod
    def find(cls, sudoku):
        yielded_coords = []

        for row, col in sudoku.empty():
            for f in column_of, row_of, square_of:
                found_hidden_single = False
                candidates = set(NUMBERS)
                for i, j in f(row, col, include=False):
                    candidates -= sudoku.get_candidates(i, j)

                for value in candidates:
                    if (row, col) not in yielded_coords:
                        yielded_coords.append((row, col))
                        yield cls(row, col, value)
                        found_hidden_single = True

                # skip the other functions
                if found_hidden_single:
                    break


class Bruteforce(SingleFieldStep):
    @classmethod
    def find(cls, sudoku):
        try:
            solution = next(bruteforce(sudoku))
        except StopIteration:
            return
        for row, col in sudoku.diff(solution):
            yield cls(row, col, solution[row, col])


@total_ordering
class NakedTuple(SolveStep):
    n = 2

    def __init__(self, coords, candidates):
        super(NakedTuple, self).__init__()

        self.coords = tuple(sorted(coords))
        self.candidates = tuple(sorted(candidates))

    def __eq__(self, other):
        return (self.coords, self.candidates) == (
                other.coords, other.candidates)

    def __lt__(self, other):
        if self.coords < other.coords:
            return True
        elif self.coords > other.coords:
            return False
        else:
            return self.candidates < other.candidates

    def __str__(self):
        return "%s at %s: %s" % (
            self.__class__.__name__, self.coords, self.candidates)

    def __repr__(self):
        return "%s(%s, %s)" % (
            self.__class__.__name__, self.coords, self.candidates)

    def build_actions(self, sudoku):
        super(NakedTuple, self).build_actions(sudoku)

        # find out, if self.coords lie in the same row, col or square
        # We can assume len(self.coords) >= 2

        # check for same row
        if self.coords[0][0] == self.coords[1][0]:
            func = row_of
        elif self.coords[0][1] == self.coords[1][1]:
            func = column_of
        else:
            func = square_of

        for (i, j) in func(*self.coords[0]):
            # skip fields, that are in the coords set
            if (i, j) in self.coords:
                continue

            to_remove = set(self.candidates) & sudoku.get_candidates(i, j)

            if to_remove:
                self.actions.append(
                    Action(Sudoku.remove_candidates, i, j, to_remove))

    @classmethod
    def find(cls, sudoku):
        # keep track of yielded steps
        yielded_coords = []

        # we work through rows, cols and quads in 3 steps, since the
        # empty fields can changed in-between
        for func in row_of, column_of, square_of:
            clist = []
            for (row, col) in sudoku.empty():
                coords = func(row, col)
                if coords not in clist:
                    clist.append(coords)
            for coords in clist:
                for step in cls.__find_at(sudoku, coords):
                    if step.coords not in yielded_coords:
                        yielded_coords.append(step.coords)
                        yield step

    @classmethod
    def __find_at(cls, sudoku, coords):
        # Create a list of fields with at least 2 and at most n candidates.
        # (We ignore naked singles here, because combinations() would
        # return a very long list otherwise.)
        n_candidates = [(row, col) for (row, col) in coords if 1 < len(
            sudoku.get_candidates(row, col)) <= cls.n]

        for fields in combinations(n_candidates, cls.n):
            all_candidates = set()
            for (row, col) in fields:
                all_candidates |= sudoku.get_candidates(row, col)

            if len(all_candidates) <= cls.n:
                # Naked Tuple found.
                yield cls(fields, all_candidates)


NakedPair = type("NakedPair", (NakedTuple,), dict(n=2))
NakedTriple = type("NakedTriple", (NakedTuple,), dict(n=3))
NakedQuad = type("NakedQuad", (NakedTuple,), dict(n=4))
NakedQuint = type("NakedQuint", (NakedTuple,), dict(n=5))


ALL_STEPS = [
    NakedSingle,
    HiddenSingle,
    NakedPair,
    NakedTriple,
    NakedQuad,
    NakedQuint,
    Bruteforce
]

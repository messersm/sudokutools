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
 * HiddenSingle
 * Bruteforce
"""

from collections import namedtuple

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
        self.actions = list(actions)

    def apply(self, sudoku):
        for action in self.actions:
            action.func(sudoku, action.row, action.col, action.value)


class SingleFieldStep(SolveStep):
    def __init__(self, row, col, value, *actions, **details):
        super(SingleFieldStep, self).__init__(*actions)
        self.row = row
        self.col = col
        self.value = value
        self.details = details

    def __eq__(self, other):
        if self.__class__ == other.__class__:
            return (self.row, self.col, self.value) == (
                other.row, other.col, other.value)
        else:
            return False

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash(repr(self))

    def __str__(self):
        return "%s at (%d, %d): %d" % (
            self.__class__.__name__, self.row, self.col, self.value)

    def __repr__(self):
        return "%s(%d, %d, %d)" % (
            self.__class__.__name__, self.row, self.col, self.value)

    @classmethod
    def expand_set_number(cls, sudoku, row, col, value, **details):
        step = cls(
            row, col, value,
            Action(Sudoku.set_number, row, col, value),
            Action(Sudoku.set_candidates, row, col, value),
            **details
        )

        for i, j in surrounding_of(row, col, include=False):
            if value in sudoku.get_candidates(i, j):
                step.actions.append(
                    Action(Sudoku.remove_candidates, i, j, {value}))

        return step


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
                yield cls.expand_set_number(sudoku, row, col, value)


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
                        yield cls.expand_set_number(sudoku, row, col, value)
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
            yield cls.expand_set_number(sudoku, row, col, solution[row, col])

ALL_STEPS = [
    NakedSingle,
    HiddenSingle,
    Bruteforce
]

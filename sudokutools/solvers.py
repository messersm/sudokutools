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
 * CalcCandidates
 * NakedSingle
 * NakedPair
 * NakedTriple
 * NakedQuad
 * NakedQuint
 * HiddenSingle
 * Bruteforce
"""

from collections import defaultdict, namedtuple
from functools import total_ordering
from itertools import combinations, product

from sudokutools.solve import calc_candidates, bruteforce
from sudokutools.sudoku import column_of, row_of, square_of, surrounding_of, \
    NUMBERS, INDICES, Sudoku


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


@total_ordering
class SolveStep(object):
    def __init__(self, clues=(), affected=(), values=()):
        self.clues = tuple(sorted(clues))
        self.affected = tuple(sorted(affected))
        self.values = tuple(sorted(values))
        self.actions = []

    def __eq__(self, other):
        return (self.clues, self.affected, self.values) == (
            other.clues, other.affected, other.values)

    def __lt__(self, other):
        return (self.clues, self.affected, self.values) < (
            other.clues, other.affected, other.values)

    def __repr__(self):
        return "%s(%s, %s, %s)" % (
            self.__class__.__name__, self.clues, self.affected, self.values)

    @classmethod
    def find(cls, sudoku):
        raise NotImplementedError("%s.find() not implemented." % cls.__name__)

    def build_actions(self, sudoku):
        raise NotImplementedError(
            "%s.build_actions() not implemented." % self.__class__.__name__)

    def apply(self, sudoku):
        if not self.actions:
            self.build_actions(sudoku)

        for action in self.actions:
            action.func(sudoku, action.row, action.col, action.value)

    @classmethod
    def apply_all(cls, sudoku):
        for step in cls.find(sudoku):
            step.apply(sudoku)


class CalculateCandidates(SolveStep):
    @classmethod
    def find(cls, sudoku):
        for row, col in product(INDICES, repeat=2):
            # ignore fields with defined candidates
            if sudoku.get_candidates(row, col):
                continue

            values = calc_candidates(sudoku, row, col)
            yield cls(((row, col),), ((row, col),), values)

    def build_actions(self, sudoku):
        row, col = self.clues[0]

        self.actions.append(
            Action(Sudoku.set_candidates, row, col, self.values))


class SingleFieldStep(SolveStep):
    def __init__(self, row, col, value):
        super(SingleFieldStep, self).__init__(
            ((row, col),), ((row, col),), (value, ))

    @classmethod
    def find(cls, sudoku):
        raise NotImplementedError("%s.find() not implemented." % cls.__name__)

    def build_actions(self, sudoku):
        row, col = self.affected[0]
        value = self.values[0]

        self.actions.append(
            Action(Sudoku.set_number, row, col, value))
        self.actions.append(
            Action(Sudoku.set_candidates, row, col, {value}))

        for i, j in surrounding_of(row, col, include=False):
            if value in sudoku.get_candidates(i, j):
                self.actions.append(
                    Action(Sudoku.remove_candidates, i, j, {value}))


class NakedSingle(SingleFieldStep):
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


class NakedTuple(SolveStep):
    n = 2

    def build_actions(self, sudoku):
        for (i, j) in self.affected:
            # skip fields, that are in the clues tuple
            if (i, j) in self.clues:
                continue

            to_remove = set(self.values) & sudoku.get_candidates(i, j)
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
                    if step.clues not in yielded_coords:
                        yielded_coords.append(step.clues)
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
                # Naked Tuple found - only yield, if actions can be applied.
                step = cls(clues=fields, affected=coords, values=all_candidates)
                step.build_actions(sudoku)
                if step.actions:
                    yield step


NakedPair = type("NakedPair", (NakedTuple,), dict(n=2))
NakedTriple = type("NakedTriple", (NakedTuple,), dict(n=3))
NakedQuad = type("NakedQuad", (NakedTuple,), dict(n=4))
NakedQuint = type("NakedQuint", (NakedTuple,), dict(n=5))


class HiddenTuple(SolveStep):
    n = 2

    def build_actions(self, sudoku):
        for row, col in self.affected:
            to_remove = sudoku.get_candidates(row, col) - set(self.values)

            if to_remove:
                self.actions.append(
                    Action(Sudoku.remove_candidates, row, col, to_remove))

    @classmethod
    def find(cls, sudoku):
        # keep track of yielded steps
        yielded_coords = []

        # we work through rows, cols and quads in 3 steps, since the
        # empty fields can changed in-between
        for func in row_of, column_of, square_of:
            clist = []
            for (i, j) in sudoku.empty():
                coords = func(i, j)
                if coords not in clist:
                    clist.append(coords)
            for coords in clist:
                for step in cls.__find_at(sudoku, coords):
                    yield step

    @classmethod
    def __find_at(cls, sudoku, coords):
        cand_coords = defaultdict(lambda: set())

        # build coordinate list for each candidate
        for cand in NUMBERS:
            for (row, col) in coords:
                if cand in sudoku.get_candidates(row, col):
                    cand_coords[cand].add((row, col))

        # create a list of numbers with at most n occurrences
        n_times = [c for c in NUMBERS if 1 < len(cand_coords[c]) <= cls.n]

        # select n numbers from the n_times list
        for numbers in combinations(n_times, cls.n):
            max_set = set()
            for num in numbers:
                max_set |= cand_coords[num]

            if len(max_set) <= cls.n:
                # hidden tuple found - only yield, if there are actions to apply
                for (row, col) in max_set:
                    step = cls(clues=coords, affected=max_set, values=numbers)
                    step.build_actions(sudoku)
                    if step.actions:
                        yield step


HiddenPair = type("HiddenPair", (HiddenTuple,), dict(n=2))
HiddenTriple = type("HiddenTriple", (HiddenTuple,), dict(n=3))
HiddenQuad = type("HiddenQuad", (HiddenTuple,), dict(n=4))
HiddenQuint = type("HiddenQuint", (HiddenTuple,), dict(n=5))


SOLVE_STEPS = [
    CalculateCandidates,
    NakedSingle,
    HiddenSingle,
    NakedPair,
    HiddenPair,
    NakedTriple,
    HiddenTriple,
    NakedQuad,
    HiddenQuad,
    NakedQuint,
    HiddenQuint,
    Bruteforce
]


def solve(sudoku, steps=SOLVE_STEPS, report=lambda step: None):
    solution = sudoku.copy()
    steps = list(steps)

    while True:
        for cls in steps:
            count = 0

            for step in cls.find(solution):
                report(step)
                step.apply(solution)
                count += 1

            if count > 0:
                break
        else:
            break

    return solution
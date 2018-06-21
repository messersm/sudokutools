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
 * HiddenPair
 * HiddenTriple
 * HiddenQuad
 * HiddenQuint
 * PointingPair
 * PointingTriple
 * XWing
 * Swordfish
 * Jellyfish
 * Bruteforce
"""

from collections import defaultdict, namedtuple
from functools import total_ordering
from itertools import combinations, product

from sudokutools.solve import init_candidates, calc_candidates, bruteforce
from sudokutools.sudoku import Sudoku


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
        """Create a new solve step.

        Args:
            clues (iterable of (int, int)): An iterable of (row, col) pairs
                                            which cause this step.
            affected (iterable of (int, int)): An iterable of (row, col)
                                               pairs which are affected by
                                               this step.
            values (iterable of int) : A list of values to apply to the
                                       affected fields.
        """
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

    def __str__(self):
        return "%s at %s: %s" % (
            self.__class__.__name__, self.clues, self.values)

    @classmethod
    def find(cls, sudoku):
        """Iterates through all possible solve steps of this class.

        Args:
            sudoku (Sudoku): The sudoku to solve.

        Yields:
            SolveStep: The next solve step.
        """

        raise NotImplementedError("%s.find() not implemented." % cls.__name__)

    def build_actions(self, sudoku):
        raise NotImplementedError(
            "%s.build_actions() not implemented." % self.__class__.__name__)

    def apply(self, sudoku):
        """Apply this solve step to the sudoku."""
        if not self.actions:
            self.build_actions(sudoku)

        for action in self.actions:
            action.func(sudoku, action.row, action.col, action.value)

    @classmethod
    def apply_all(cls, sudoku):
        """Apply all possible steps of this class to the sudoku."""
        for step in cls.find(sudoku):
            step.apply(sudoku)


class CalculateCandidates(SolveStep):
    """Calculates the candidates of fields."""
    @classmethod
    def find(cls, sudoku):
        for row, col in sudoku:
            # ignore fields with defined candidates
            if sudoku.get_candidates(row, col):
                continue

            values = calc_candidates(sudoku, row, col)
            yield cls(((row, col),), ((row, col),), values)

    def build_actions(self, sudoku):
        row, col = self.clues[0]

        self.actions.append(
            Action(Sudoku.set_candidates, row, col, self.values))


class _SingleFieldStep(SolveStep):
    """Represents a solve method, which sets a single field."""

    def __init__(self, row, col, value):
        super(_SingleFieldStep, self).__init__(
            ((row, col),), ((row, col),), (value, ))

    def __repr__(self):
        row, col = self.clues[0]
        value = self.values[0]
        return "%s(%d, %d, %d)" % (self.__class__.__name__, row, col, value)

    def __str__(self):
        return "%s at %s: %s" % (
            self.__class__.__name__, self.clues[0], self.values[0])

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

        for i, j in sudoku.surrounding_of(row, col, include=False):
            if value in sudoku.get_candidates(i, j):
                self.actions.append(
                    Action(Sudoku.remove_candidates, i, j, {value}))


class NakedSingle(_SingleFieldStep):
    """Finds naked singles in a sudoku.

    A naked single is a field with only one candidate.

    The field can be set to this candidate and this candidate
    can be removed from all fields in the same row, column and box.
    """
    @classmethod
    def find(cls, sudoku):
        for row, col in sudoku.empty():
            candidates = sudoku.get_candidates(row, col)
            if len(candidates) == 1:
                for value in candidates:
                    break
                yield cls(row, col, value)


class HiddenSingle(_SingleFieldStep):
    """Finds hidden singles in a sudoku.

    A hidden single is a field containing a candidate which
    exists in no other fields in the same row, column or box.

    The field can be set to this candidate and this candidate
    can be removed from all fields in the same row, column and box.
    """
    @classmethod
    def find(cls, sudoku):
        yielded_coords = []

        for row, col in sudoku.empty():
            for f in sudoku.column_of, sudoku.row_of, sudoku.box_of:
                found_hidden_single = False
                candidates = set(sudoku.numbers)
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


class Bruteforce(_SingleFieldStep):
    """Solve the sudoku using brute force.

    Bruteforce simply works by trial and error testing each
    combination of valid candidates in a field until a
    solution has been found.
    """
    @classmethod
    def find(cls, sudoku):
        try:
            solution = next(bruteforce(sudoku))
        except StopIteration:
            return
        for row, col in sudoku.diff(solution):
            yield cls(row, col, solution[row, col])


class NakedTuple(SolveStep):
    """Finds naked tuples in a sudoku.

    A naked tuple is a set of n fields in a row, column or box,
    which (in unison) contain a set of at most n candidates.

    These candidates can be removed from all fields in the
    same row, column or box.
    """
    n = 2

    def build_actions(self, sudoku):
        for (i, j) in self.affected:
            to_remove = set(self.values) & sudoku.get_candidates(i, j)
            self.actions.append(
                Action(Sudoku.remove_candidates, i, j, to_remove)
            )

    @classmethod
    def find(cls, sudoku):
        # keep track of yielded steps
        yielded_coords = []

        # we work through rows, cols and quads in 3 steps, since the
        # empty fields can changed in-between
        for func in sudoku.row_of, sudoku.column_of, sudoku.box_of:
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
                affected = [(r, c) for r, c in coords if (r, c) not in fields
                            and set(all_candidates)& sudoku.get_candidates(r, c)]

                if affected:
                    step = cls(
                        clues=fields, affected=affected, values=all_candidates)
                    yield step


NakedPair = type("NakedPair", (NakedTuple,), dict(n=2))
NakedTriple = type("NakedTriple", (NakedTuple,), dict(n=3))
NakedQuad = type("NakedQuad", (NakedTuple,), dict(n=4))
NakedQuint = type("NakedQuint", (NakedTuple,), dict(n=5))


class HiddenTuple(SolveStep):
    """Finds hidden tuples in a sudoku.

    A hidden tuple is a set of n fields in a row, column or box,
    which (in unison) contain a set of at most n candidates, which
    are present in no other fields of the same row, column or box.

    All other candidates can be removed from these fields.
    """
    n = 2

    def build_actions(self, sudoku):
        for row, col in self.affected:
            to_remove = sudoku.get_candidates(row, col) - set(self.values)
            self.actions.append(
                Action(Sudoku.remove_candidates, row, col, to_remove))

    @classmethod
    def find(cls, sudoku):
        # keep track of yielded steps
        yielded_coords = []

        # we work through rows, cols and quads in 3 steps, since the
        # empty fields can changed in-between
        for func in sudoku.row_of, sudoku.column_of, sudoku.box_of:
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
        for cand in sudoku.numbers:
            for (row, col) in coords:
                if cand in sudoku.get_candidates(row, col):
                    cand_coords[cand].add((row, col))

        # create a list of numbers with at most n occurrences
        n_times = [c for c in sudoku.numbers if 1 < len(cand_coords[c]) <= cls.n]

        # select n numbers from the n_times list
        for numbers in combinations(n_times, cls.n):
            max_set = set()
            for num in numbers:
                max_set |= cand_coords[num]

            if len(max_set) <= cls.n:
                # hidden tuple found - only yield, if there are actions to apply
                for (row, col) in max_set:
                    affected = [(r, c) for r, c in max_set
                                if sudoku.get_candidates(r, c) - set(numbers)]

                    if affected:
                        yield cls(clues=coords, affected=affected, values=numbers)

HiddenPair = type("HiddenPair", (HiddenTuple,), dict(n=2))
HiddenTriple = type("HiddenTriple", (HiddenTuple,), dict(n=3))
HiddenQuad = type("HiddenQuad", (HiddenTuple,), dict(n=4))
HiddenQuint = type("HiddenQuint", (HiddenTuple,), dict(n=5))


class PointingTuple(SolveStep):
    n = 2

    @classmethod
    def find(cls, sudoku):
        # reducing row or column candidates
        for box in sudoku.indices:
            for step in cls.__find_in_box(sudoku, box):
                yield step

        # reducing box candidates
        for x in sudoku.indices:
            for step in cls.__find_in_row_and_column(sudoku, x):
                yield step

    @classmethod
    def __find_in_row_and_column(cls, sudoku, x):
        for f in sudoku.row_of, sudoku.column_of:
            coords = f(x, x)

            for candidate in sudoku.numbers:
                clues = [(r, c) for r, c in coords
                         if candidate in sudoku.get_candidates(r, c)]

                # skip, if this doesn't have the correct number of fields
                # (e.g. we have a pair, but want a triple)
                if len(clues) != cls.n:
                    continue

                # if all fields with this candidate lie in the same
                # box, remove this candidate from all other fields
                # in the box
                if len(set([sudoku.box_at(r, c) for r, c in clues])) == 1:
                    affected = [(r, c) for r, c in sudoku.box_of(*clues[0])
                                if (r, c) not in clues
                                and candidate in sudoku.get_candidates(r, c)]

                    if affected:
                        yield cls(
                            clues=clues, affected=affected, values=(candidate,))


    @classmethod
    def __find_in_box(cls, sudoku, box):
        row = (box // sudoku.height) * sudoku.height
        col = (box % sudoku.height) * sudoku.width

        box_coords = sudoku.box_of(row, col)

        for candidate in sudoku.numbers:
            clues = [(r, c) for r, c in box_coords
                     if candidate in sudoku.get_candidates(r, c)]

            # skip, if this doesn't have the correct number of fields
            # (e.g. we have a pair, but want a triple)
            if len(clues) != cls.n:
                continue

            # if all fields with this candidate lie in the same row
            # remove this candidate from all other fields in the same row
            if len(set([r for r, c in clues])) == 1:
                affected = [(r, c) for r, c in sudoku.row_of(*clues[0])
                            if (r, c) not in clues
                            and candidate in sudoku.get_candidates(r, c)]

            # if all fields with this candidate lie in the same column
            # remove this candidate from all other fields in the same column
            elif len(set([c for r, c in clues])) == 1:
                affected = [(r, c) for r, c in sudoku.column_of(*clues[0])
                            if (r, c) not in clues
                            and candidate in sudoku.get_candidates(r, c)]
            else:
                affected = []

            if affected:
                yield cls(
                    clues=clues, affected=affected, values=(candidate,))

    def build_actions(self, sudoku):
        val = self.values[0]

        for r, c in self.affected:
            self.actions.append(
                Action(Sudoku.remove_candidates, r, c, self.values))

PointingPair = type("PointingPair", (PointingTuple,), dict(n=2))
PointingTriple = type("PointingTriple", (PointingTuple,), dict(n=3))


class BasicFish(SolveStep):
    n = 2

    @classmethod
    def find(cls, sudoku):
        variants = ((0, sudoku.row_of, sudoku.column_of),
                    (1, sudoku.column_of, sudoku.row_of))

        for item, candidate in product(variants, sudoku.numbers):
            for step in cls.__find_for_candidate(sudoku, candidate, *item):
                yield step

    @classmethod
    def __find_for_candidate(
            cls, sudoku, candidate, offset, base_func, cover_func):

        # fields with this candidate, keyed by their index.
        fields = {}
        for i in sudoku.indices:
            fields[i] = [(r, c) for r, c in base_func(i, i)
                         if candidate in sudoku.get_candidates(r, c)]

        valid_indices = [i for i in fields if 2 <= len(fields[i]) <= cls.n]

        for indices in combinations(valid_indices, cls.n):
            base_fields = []
            for i in indices:
                base_fields.extend(fields[i])

            other_counts = defaultdict(lambda: 0)
            other_offset = (offset + 1) % 2
            for coord in base_fields:
                other_counts[coord[other_offset]] += 1

            # The other coordinate only appears once,
            # so this is not a valid fish
            if min(other_counts.values()) < 2:
                continue
            # There are more than cls.n other coordinates,
            # so this is not a valid fish
            if len(other_counts) > cls.n:
                continue

            covered = []
            for val in other_counts:
                covered.extend(cover_func(val, val))

            affected = [(r, c) for r, c in covered
                        if (r, c) not in base_fields
                        and candidate in sudoku.get_candidates(r, c)]

            if affected:
                yield cls(
                    clues=base_fields,
                    affected=affected,
                    values=(candidate,)
                )

    def build_actions(self, sudoku):
        for r, c in self.affected:
            self.actions.append(
                Action(Sudoku.remove_candidates, r, c, self.values))


XWing = type("XWing", (BasicFish,), dict(n=2))
Swordfish = type("Swordfish", (BasicFish,), dict(n=3))
Jellyfish = type("Jellyfish", (BasicFish,), dict(n=4))


# A list of available solve methods (in the order, they're used by solve())
SOLVERS = [
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
    PointingPair,
    PointingTriple,
    XWing,
    Swordfish,
    Jellyfish,
    Bruteforce,
]


def solve(sudoku, report=lambda step: None):
    """Solve the sudoku and return the solution.

    Args:
        sudoku (Sudoku): The sudoku to solve.
        report (callable): A function taking a single argument (the current
                           step), which can be used as a callback.

    Returns:
        Sudoku: The solution of the sudoku.
    """

    solution = sudoku.copy()
    init_candidates(solution, filled_only=True)

    while True:
        for cls in SOLVERS:
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

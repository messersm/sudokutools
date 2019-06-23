from __future__ import print_function

import inspect
import os
import platform
import sys

from ast import literal_eval
from collections import namedtuple

from sudokutools import __version__
from sudokutools.analyze import rate, is_solved, find_conflicts
from sudokutools.notation import decode_action, encode
from sudokutools.generate import generate, generate_from_template
from sudokutools.solve import bruteforce, init_candidates
from sudokutools.solvers import hints
from sudokutools.sudoku import Sudoku, view

if sys.version_info[0] <= 2:
    input = raw_input


class GameShell(object):
    def __init__(self):
        self.running = True

        self.settings = {
            "autocheck": (False, "Automatically check for cells different from the solution."),
            "autoconflicts": (True, "Automatically check for conflicts."),
            "autoremove": (True, "Automatically remove candidates in other cells if a number is set."),
            "autoset": (True, "Automatically set the number of a cell if only one candidate remains."),
            "dim": ((3, 3), "The box dimensions of a new Sudoku."),
            "rating": ((1, 10), "Minimal and maximum rating of a new Sudoku.")
        }

        self.hints = None
        self.hinted_sudoku = None

        # used for undo and redo:
        self.sudokus = []
        self.index = 0

        self.solution = None

    def startup(self):
        print("sudokutools game shell %s" % __version__)
        print("For a list of available commands type: help")

        self.sudokus = [generate()]
        self.index = 0
        self.solution = next(bruteforce(self.sudokus[0]))
        print("Generating new sudoku. Rating: %d/10" % rate(self.sudokus[0]))

    def run(self):
        self.startup()

        last_command = None

        while self.running:
            sudoku = self.sudokus[self.index].copy(include_candidates=True)
            print(view(sudoku) + "\n")
            print("> ", end="")
            line = input()
            splitted = line.split()
            command = splitted[0]

            if command == "hint":
                if self.hints is None or self.hinted_sudoku != sudoku:
                    self.hinted_sudoku = sudoku.copy(include_candidates=True)
                    self.hints = hints(sudoku)
                try:
                    print(next(self.hints))
                except StopIteration:
                    print("No more hints available.")
            elif command == "candidates":
                init_candidates(sudoku)
            elif command == "conflicts":
                listed = []

                for (r1, c1), (r2, c2), v in find_conflicts(sudoku):
                    conflict = {(r1, c1), (r2, c2)}, v
                    if conflict in listed:
                        continue
                    else:
                        listed.append(conflict)

                    s = "[F]" + encode(
                        ((r1, c1), ), sudoku.width, sudoku.height)
                    s += " = " + encode(
                        ((r2, c2), ), sudoku.width, sudoku.height)
                    s += " = " + str(v)
                    print(s)
            elif command == "settings":
                for key in sorted(self.settings):
                    value, desc = self.settings[key]
                    s = "%s = %s" % (key, value)
                    s = s.ljust(20, " ")
                    s += " # %s" % desc
                    print(s)
            elif command == "check":
                for coord in sudoku:
                    value = sudoku[coord]
                    if value != 0 and value != self.solution[coord]:
                        s = "[F] " + encode(
                            (coord, ), sudoku.width, sudoku.height)
                        s += " = " + str(value)
                        print(s)
            elif command == "undo":
                if self.index == 0:
                    print("Nothing to undo.")
                else:
                    self.index -= 1
            elif command == "redo":
                if self.index + 1 == len(self.sudokus):
                    print("Nothing to redo.")
                else:
                    self.index += 1
            else:
                try:
                    action = decode_action(
                        line, sudoku.width, sudoku.height)
                    action(sudoku)
                except ValueError as e:
                    print(e)

            # add the new sudoku to the sudokus list, if anything changed.
            if command not in ("undo", "redo"):
                if not sudoku.equals(self.sudokus[self.index], candidates=True):
                    self.sudokus = self.sudokus[:self.index + 1]
                    self.sudokus.append(sudoku)
                    self.index += 1


#
# WARNING: Serious meta-programming incoming. :)
#
def signature_str(func):
    """Return a signature string for func, which is suitable for the shell.

    Example:
        >>> def my_func(a, b=3):
        ...     pass
        >>> signature_str(my_func)
        'a b=3'
    """
    arg_str = []
    spec = inspect.getargspec(func)
    args, defaults = spec.args, spec.defaults

    # ignore first argument on methods.
    if inspect.ismethod(func):
        args = args[1:]

    for i, name in enumerate(args):
        if spec.defaults and i >= len(args) - len(defaults):
            j = i - len(defaults)
            arg_str.append("%s=%s" % (name, repr(defaults[j])))
        else:
            arg_str.append(name)

    return " ".join(arg_str)


def parse(s):
        """Parses command in s and returns a tuple

        Args:
            s: The string to parse.

        Returns:
            (callable, [], [], {}): func, special_args, args, kwargs
        """
        special_args = []
        args = []
        kwargs = {}

        items = s.split(" ")
        funcname = items[0]

        for item in items[1:]:
            try:
                if "=" in item:
                    name, value = item.split('=', 1)
                    kwargs[name] = literal_eval(value)
                else:
                    # Positional arguments could
                    # also be a keywords or a commands.
                    value = item

                    if value in COMMANDS:
                        args.append(Command(value))
                    elif value in SHELL_KEYWORDS:
                        args.append(Keyword(value))
                    else:
                        args.append(literal_eval(value))

            except (SyntaxError, ValueError):
                raise ValueError("Invalid argument: %s " % value +
                                 "(Did you forget quotation marks?)")

        # resolve the function object and check for special args
        try:
            entry = COMMANDS[funcname]
        except KeyError:
            raise KeyError(
                "Unknown command: %s. Type 'help' for a list of commands." %
                funcname)

        func = entry[0]

        # add special args, if present.
        # we MUST NOT resolve the special args right now,
        # because the referenced objects (the sudoku), may have changed
        # at exec time. So here we just check, if the special arg is valid.
        for name in entry[1:]:
            if name not in SPECIAL_ARGS:
                raise ValueError("Unknown special name '%s'" % name)
            else:
                special_args.append(name)

        return func, special_args, args, kwargs


def clear():
    """Clear the terminal screen."""

    # For some reason, the standard VT100 control
    # sequence doesn't work on Windows.
    if platform.system() == "Windows":
        os.system("cls")
    else:
        print("\033[H\033[J", end="")


class Shell(object):
    def __init__(
            self, interactive=None, infile=sys.stdin, outfile=sys.stdout,
            commands=None, keywords=None):
        # automatically determine, if this is an interactive shell
        self.infile = infile
        self.outfile = outfile

        if commands:
            self.commands = commands
        else:
            self.commands = COMMANDS

        if keywords:
            self.keywords = keywords
        else:
            self.keywords = SHELL_KEYWORDS

        if interactive is None:
            if self.infile.isatty():
                self.interactive = True
            else:
                self.interactive = False
        else:
            self.interactive = interactive

        if self.interactive:
            self.command_prompt = "> "
            self.prompt = self.command_prompt
        else:
            self.command_prompt = ""
            self.prompt = self.command_prompt

        # some state
        self.sudoku = Sudoku()
        self.running = True
        self.__loop_n = None
        self.__loop_command_list = []
        self.stack = []

    def _print(self, s, end='\n'):
        self.outfile.write(s + end)
        self.outfile.flush()

    def error(self, s):
        sys.stderr.write("Error: %s\n" % s)
        sys.stderr.flush()
        if not self.interactive:
            sys.exit(1)

    def execute(self, func, special_args, args, kwargs):
        # resolve special args, if present
        d = {"sudoku": self.sudoku, "shell": self}
        all_args = [d[name] for name in special_args]
        all_args.extend(args)

        try:
            result = func(*all_args, **kwargs)
            if isinstance(result, Sudoku):
                self.sudoku = result
            elif result is None:
                pass
            else:
                self._print(result)
        except Exception as e:
            self.error(str(e))
            # raise

    def execute_line(self, line):
        for s in line.split(';'):
            s = s.strip()

            try:
                command = parse(s)
                # always exit
                if command[0] == Shell.exit_command:
                    self.execute(*command)
                # if we're defining a loop, only execute loop commands.
                elif self.__loop_n and command[0] != Shell.loop_command:
                    self.__loop_command_list.append(command)
                else:
                    self.execute(*command)
            except KeyError as e:
                self.error(e)
            except ValueError as e:
                self.error(e)

    def run(self):
        if self.interactive:
            self._print("sudokutools shell %s" % __version__)
            self._print("For a list of available commands type: help")

        lines = ""
        while self.running:
            try:
                self._print(self.prompt, end='')
                line = self.infile.readline()
            except KeyboardInterrupt:
                if self.interactive:
                    self._print("\nUse 'exit' to leave the shell.")
                    line = "\n"
                else:
                    sys.exit(2)

            try:
                # readline() doesn't raise EOFError, but
                # returns an empty line at EOF.
                if not line:
                    if self.interactive:
                        self._print("")
                    break
                line = line.replace('\n', '')

                # remove comments
                idx = line.find('#')
                if idx >= 0:
                    line = line[:idx]

                # remove whitespace
                line = line.strip()

                # handle line wraps
                if line.endswith('\\'):
                    lines += line[:-1]
                else:
                    lines += line

                    # ignore empty lines
                    if lines:
                        self.execute_line(lines)
                    lines = ""
            except KeyboardInterrupt:
                self._print("")

                if not self.interactive:
                    sys.exit(2)

    def help_command(self, command=None, verbose=True):
        """Show help for command (or all commands, if no name is given)."""
        if command:
            s = ""

            func = COMMANDS[command.name][0]

            # use __init__, if func is a class
            if inspect.isclass(func):
                func = func.__init__

            sig = signature_str(func)

            if func.__doc__ is None:
                help_str = "(Not documented)"
            else:
                help_str = func.__doc__.split("\n")[0].strip()

            s += " ".join((command.name, sig)) + ": " + help_str

            if verbose and func.__doc__:
                s += "\n".join(func.__doc__.split('\n')[1:])
        else:
            s = ""

            for section, names in COMMANDS_HELP:
                s += section + "\n"
                for name in names:
                    # Add the first line of the full help
                    s += " - "
                    s += self.help_command(Command(name), verbose=False) + "\n"
                # newline at end of section
                s += "\n"

            s += "NOTE: The 'sudoku' argument will be supplied automatically."

        return s

    def loop_command(self, n):
        """Define (n is an int) or run (n is 'end') a loop."""

        if n == Keyword("end"):
            if not self.__loop_n:
                return self.error("No loop defined.")

            self.prompt = self.command_prompt

            # run commands
            for _ in range(self.__loop_n):
                for command in self.__loop_command_list:
                    self.execute(*command)

            self.__loop_n = None
            self.__loop_command_list = []
        else:
            try:
                n = int(n)
                assert n > 0
            except (ValueError, AssertionError):
                return self.error("loop command n must be int > 0, got %s" % n)

            if self.__loop_n:
                return self.error("Run current loop first ('loop end').")

            if self.interactive:
                self.prompt = "loop %d> " % n
            self.__loop_n = n

    def exit_command(self):
        """Exit the sudokutools shell."""
        self.running = False

    def stack_command(self):
        """Show the number of sudokus on the stack."""
        return "stack has %d sudokus" % len(self.stack)

    def push_command(self):
        """Push the current sudoku to the stack."""
        self.stack.append(self.sudoku.copy(include_candidates=True))

    def pop_command(self, position=None):
        """Pop the sudoku at 'position' from the stack"""

        if not self.stack:
            return self.error("stack is empty")

        if position is None:
            position = len(self.stack) - 1
        else:
            try:
                position = int(position)
                assert 0 <= position < len(self.stack)
            except (ValueError, AssertionError):
                return self.error(
                    "0 <= position < %d" % len(self.stack))

        self.sudoku = self.stack.pop(position)

    def solve_command(self, sudoku):
        """Solve the current sudoku."""
        return next(bruteforce(sudoku))


SPECIAL_ARGS = ("sudoku", "shell")
COMMANDS = {
    # Creating sudokus
    "new": (Sudoku, ),
    "generate": (generate, ),
    "generate_from_template": (generate_from_template, "sudoku"),
    "decode": (Sudoku.decode, ),

    # Changing the current sudoku
    "get": (Sudoku.get_number, "sudoku"),
    "set": (Sudoku.set_number, "sudoku"),
    "set_candidates": (Sudoku.set_candidates, "sudoku"),
    "get_candidates": (Sudoku.get_candidates, "sudoku"),
    "remove_candidates": (Sudoku.remove_candidates, "sudoku"),
    "init_candidates": (init_candidates, "sudoku"),

    # printing
    "encode": (Sudoku.encode, "sudoku"),
    "print": (Sudoku.__str__, "sudoku"),
    "clear": (clear,),
    "view": (view, "sudoku"),

    # solving
    "solve": (Shell.solve_command, "shell", "sudoku"),

    # advanced
    "loop": (Shell.loop_command, "shell"),
    "stack": (Shell.stack_command, "shell"),
    "push": (Shell.push_command, "shell"),
    "pop": (Shell.pop_command, "shell"),

    # shell
    "help": (Shell.help_command, "shell"),
    "exit": (Shell.exit_command, "shell"),
}

# helper tuple to define the sections for the help command
COMMANDS_HELP = (
    ("Creating sudokus:",
        ("new", "decode", "generate", "generate_from_template")),
    ("Setting and getting numbers and candidates:",
        ("get", "set", "get_candidates", "set_candidates", "remove_candidates",
         "init_candidates")),
    ("Printing:", ("encode", "print", "clear", "view")),
    ("Solving:", ("solve",)),
    ("Advanced:", ("loop", "stack", "push", "pop")),
    ("Other commands:", ("help", "exit"))
)

# Defines keywords for the shell.
Keyword = namedtuple("Keyword", ["name"])
Command = namedtuple("Command", ["name"])

SHELL_KEYWORDS = {
    "end": Keyword("end")
}

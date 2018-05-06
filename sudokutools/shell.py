from ast import literal_eval
import inspect
import sys

from sudokutools import __version__
from sudokutools.generate import generate, generate_from_template
from sudokutools.solve import bruteforce
from sudokutools.sudoku import Sudoku

if sys.version_info[0] <= 2:
    input = raw_input


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
            if "=" in item:
                name, value = item.split('=', 1)
                try:
                    kwargs[name] = literal_eval(value)
                except (SyntaxError, ValueError):
                    kwargs[name] = value
            else:
                try:
                    args.append(literal_eval(item))
                except (SyntaxError, ValueError):
                    args.append(item)

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


class Shell(object):
    def __init__(self, interactive=None, infile=sys.stdin, outfile=sys.stdout):
        # automatically determine, if this is an interactive shell
        self.infile = infile
        self.outfile = outfile

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
                # if we're defining a loop, only execute loop commands.
                if self.__loop_n and command[0] != Shell.loop_command:
                    self.__loop_command_list.append(command)
                else:
                    self.execute(*command)
            except KeyError as e:
                self.error(e)

    def run(self):
        if self.interactive:
            self._print("sudokutools shell %s" % __version__)
            self._print("For a list of available command type: help")

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

    def clear_command(self):
        """Clear the terminal screen."""
        self._print("\033[H\033[J", end="")


    def help_command(self, command=None, verbose=True):
        """Show help for command (or all commands, if no name is given)."""
        if command:
            if command not in COMMANDS:
                return self.error(
                    "Unknown command: %s. Type 'help' for a list of commands." %
                    command)

            s = ""

            func = COMMANDS[command][0]

            # use __init__, if func is a class
            if inspect.isclass(func):
                func = func.__init__

            sig = signature_str(func)

            if func.__doc__ is None:
                help_str = "(Not documented)"
            else:
                help_str = func.__doc__.split("\n")[0].strip()

            s += " ".join((command, sig)) + ": " + help_str

            if verbose and func.__doc__:
                s += "\n".join(func.__doc__.split('\n')[1:])

        else:
            s = ""

            for section, names in COMMANDS_HELP:
                s += section + "\n"
                for command in names:
                    # Add the first line of the full help
                    s += " - "
                    s += self.help_command(command, verbose=False) + "\n"
                # newline at end of section
                s += "\n"

            s += "NOTE: The 'sudoku' argument will be supplied automatically."

        return s

    def loop_command(self, n):
        """Define (n is an int) or run (n is 'end') a loop."""

        if n == "end":
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

    # printing
    "encode": (Sudoku.encode, "sudoku"),
    "print": (Sudoku.__str__, "sudoku"),
    "clear": (Shell.clear_command, "self"),

    # solving
    "bruteforce": (bruteforce, "sudoku"),

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
        ("get", "set", "get_candidates", "set_candidates", "remove_candidates")),
    ("Printing:", ("encode", "print", "clear")),
    ("Solving:", ("bruteforce",)),
    ("Advanced:", ("loop", "stack", "push", "pop")),
    ("Other commands:", ("help", "exit"))
)

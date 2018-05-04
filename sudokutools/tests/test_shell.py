from itertools import product
from unittest import TestCase

from sudokutools.sudoku import Sudoku, INDICES
from sudokutools.shell import Shell, parse, COMMANDS, COMMANDS_HELP


class ParseTests(TestCase):
    def test_args(self):
        self.assertEqual(
            parse("exit 1 2 5 None 2,3,4"),
            (Shell.exit_command, ["shell"], [1, 2, 5, None, (2, 3, 4)], {})
        )

    def test_kwargs(self):
        self.assertEqual(
            parse("exit 2 1 4 2 max_size=32 include=False"), (
                Shell.exit_command,
                ["shell"],
                [2, 1, 4, 2],
                {"max_size": 32, "include":False})
        )


class HelpTests(TestCase):
    def test_help_complete(self):
        """The Shell provides help for every command."""
        count = 0
        for section, names in COMMANDS_HELP:
            count += len(names)

        self.assertEqual(count, len(COMMANDS))


class CommandTests(TestCase):
    def test_exit_works(self):
        """The exit command works."""
        shell = Shell()
        shell.execute(*parse("exit"))
        self.assertEqual(shell.running, False)

    def test_new_works(self):
        """The new command works."""
        shell = Shell()
        shell.sudoku[0, 0] = 4
        shell.execute(*parse("new"))
        self.assertEqual(len(shell.sudoku), 0)

    def test_generate_works(self):
        """The generate command works."""
        shell = Shell()
        shell.execute(*parse("generate"))
        self.assertGreater(len(shell.sudoku), 0)

    def test_generate_min_count(self):
        """The generate command respects the min_size argument."""
        shell = Shell()
        shell.execute(*parse("generate min_count=60"))
        self.assertGreaterEqual(len(shell.sudoku), 60)

    def test_generate_symmetry(self):
        """The generate command respects the symmetry argument."""
        shell = Shell()
        shell.execute(*parse("generate symmetry='mirror-xy'"))
        for row, col in product(INDICES, repeat=2):
            self.assertEqual(
                bool(shell.sudoku[row, col]),
                bool(shell.sudoku[row, 8 - col])
            )
            self.assertEqual(
                bool(shell.sudoku[row, col]),
                bool(shell.sudoku[8 - row, 8 - col])
            )
            self.assertEqual(
                bool(shell.sudoku[row, col]),
                bool(shell.sudoku[8 - row, col])
            )


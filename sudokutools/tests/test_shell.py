from unittest import TestCase

from sudokutools.sudoku import Sudoku
from sudokutools.shell import Shell, parse


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

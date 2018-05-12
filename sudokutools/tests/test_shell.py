from unittest import TestCase

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


class ExitTests(TestCase):
    def test_exit_in_loop(self):
        """The Shell exits, even while defining a loop."""
        shell = Shell()
        shell.execute_line("loop 3")
        shell.execute_line("exit")
        self.assertEqual(shell.running, False)

# A list of commands, that should succeed.
SHELL_COMMANDS_SUCCEED = [
    "new",
    "decode '008000000000000001200140050000200060070001503400060017093028070840000000002010000'",
    "generate min_count=60",
    "generate min_count=60; generate_from_template tries=-1",
    "get 0 0",
    "set 0 0 8",
    "get_candidates 0 0",
    "set_candidates 0 0 5,6",
    "remove_candidates 0 0 1,2",
    "new; encode",
    "new; print",
    "clear",
    "generate; solve",
    "loop 3; new; loop end",
    "push",
    "push; pop",
    "push; pop 0",
    "help",
    "exit"
]

# A list of commands, that should fail.
SHELL_COMMANDS_FAIL = [
    "new sudoku",
    "decode '008000000000000001200140050000200060070001503400060017093028070840000000002010000 please'",
    "generate min_count=60 rating='evil'",
    "new; generate_from_template tries=1",
    "get 0 0 3",
    "set 20 20 8",
    "get_candidates 20 20",
    "set_candidates 20 20 5,6",
    "remove_candidates 20 20 1,2",
    "new; encode 1",
    "new; print 2",
    "clear 'screen'",
    "generate; solve 'sudoku'",
    "loop 3; loop 3; loop end",
    "push 20",
    "pop",
    "push; pop 1",
    "help 'me' 'please'",
    "exit 'now'",
    "unknown_command"
]


class CommandTests(TestCase):
    def test_commands_succeed(self):
        """The shell executes valid commands without error."""

        def print_overwrite(*args, **kwargs):
            pass

        def error_overwrite(*args, **kwargs):
            error_overwrite.called = True

        shell = Shell()
        shell._print = print_overwrite
        shell.error = error_overwrite

        for command in SHELL_COMMANDS_SUCCEED:
            error_overwrite.called = False
            shell.execute_line(command)
            self.assertEqual(error_overwrite.called, False, command)

    def test_commands_fail(self):
        """The shell executes invalid commands with an error."""
        def print_overwrite(*args, **kwargs):
            pass

        def error_overwrite(*args, **kwargs):
            error_overwrite.called = True

        shell = Shell()
        shell._print = print_overwrite
        shell.error = error_overwrite

        for command in SHELL_COMMANDS_FAIL:
            error_overwrite.called = False
            shell.execute_line(command)
            self.assertEqual(error_overwrite.called, True, command)

from __future__ import print_function

import argparse
import sys

from sudokutools.shell import Shell


def main():
    """Run the sudokutools shell."""

    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument(
        "filename", nargs="?",
        help="If provided, commands will be read from <filename>.")
    parser.add_argument(
        "-c", dest="command",
        help="Execute COMMAND instead of starting an interactive shell. " +
             "(Ignored, if filename is given.)")

    arguments = parser.parse_args()

    # read commands from filename
    if arguments.filename:
        try:
            with open(arguments.filename) as f:
                Shell(infile=f).run()
        except IOError as e:
            print(e, file=sys.stderr)
            sys.exit(1)

    elif arguments.command:
        Shell(interactive=False).execute_line(arguments.command)
    # read commands from stdin
    else:
        Shell().run()


if __name__ == '__main__':
    main()

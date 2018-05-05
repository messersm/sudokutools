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

    namespace = parser.parse_args()

    # read commands from filename
    if namespace.filename:
        try:
            with open(namespace.filename) as f:
                Shell(infile=f).run()
        except IOError as e:
            print(e, file=sys.stderr)
            sys.exit(1)

    # read commands from stdin
    else:
        Shell().run()


if __name__ == '__main__':
    main()

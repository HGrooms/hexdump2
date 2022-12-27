"""
Main function module for hexdump2
"""
import argparse
import sys
from os import linesep
from pathlib import Path

try:
    # Python 3.8+ should have this module
    from importlib.metadata import version
except ModuleNotFoundError:
    # For Python 3.6 and 3.7
    from importlib_metadata import version

from hexdump2 import hexdump


def _setup_arg_parser():
    """Creates argument parser for main function.

    :return: argparse argument parser object
    """

    def _auto_int(value):
        try:
            return int(value, 0)
        except ValueError as e_auto_int:
            raise argparse.ArgumentTypeError(
                f"input cannot be converted to int type: {value}"
            ) from e_auto_int

    parser = argparse.ArgumentParser(
        prog="hexdump",
        description="An imperfect replica of hexdump -C",
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {version('hexdump2')}"
    )
    parser.add_argument(
        "-n",
        dest="length",
        help="Interpret only length bytes of input.",
        type=_auto_int,
        required=False,
    )
    parser.add_argument(
        "-s",
        dest="offset",
        help="Skip offset bytes from the beginning of the input.",
        type=_auto_int,
        required=False,
    )
    parser.add_argument(
        "-l",
        dest="color",
        help="Color output",
        action="store_true",
    )
    parser.add_argument(
        "-v",
        dest="verbose_output",
        help="Cause Hexdump2 to display all lines; otherwise similar lines are shown with a `*`",
        action="store_false",
    )
    parser.add_argument(
        "file",
        help="One or more files to process. Each output is separated by a newline.",
        type=Path,
        nargs="+",
    )

    return parser


def main():
    """Main function run by console script hexdump2 or hd2.  Also run by `python -m hexdump2` on
    command line.
    :return: system exit return code.
    """
    parser = _setup_arg_parser()
    args = parser.parse_args()

    try:
        for file in args.file:
            with file.open("rb") as file_obj:
                file_size = file.lstat().st_size
                read_start = args.offset if args.offset is not None else 0
                length = args.length if args.length is not None else file_size

                hexdump(
                    file_obj.read(length),
                    offset=read_start,
                    collapse=args.verbose_output,
                    color=args.color,
                )
    except KeyboardInterrupt:
        # Caught interrupt; print a newline to make sure we're clear.
        print("")

    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        raise SystemError(f"Caught exception in main:{linesep}{e}") from e

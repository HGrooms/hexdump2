import argparse
import sys
from os import linesep, path, pardir
from pathlib import Path

from hexdump2 import hexdump

# Duplicate code because non-installed running of commandline fails
# Use double-underscores to hide these from auto-complete imports
__parent_dir__ = path.abspath(path.join(__file__, pardir))
with open(path.join(__parent_dir__, "VERSION")) as __version_file__:
    __version__ = __version_file__.read().strip()


def setup_arg_parser():
    def _auto_int(value):
        try:
            return int(value, 0)
        except ValueError:
            raise argparse.ArgumentTypeError(
                f"input cannot be converted to int type: {value}"
            )

    parser = argparse.ArgumentParser(
        prog="hexdump",
        description="An imperfect replica of hexdump -C",
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
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
        '-l',
        dest="color",
        help="Color output",
        action='store_true',
    )
    parser.add_argument(
        '-a',
        dest='collapse',
        help='Do NOT collapse multiple lines with a `*`',
        action='store_false',
    )
    parser.add_argument(
        "file",
        help="One or more files to process. Each output is separated by a newline.",
        type=Path,
        nargs="+",
    )

    return parser


def main():
    parser = setup_arg_parser()
    args = parser.parse_args()

    try:
        for file in args.file:
            with file.open("rb") as fh:
                file_size = file.lstat().st_size
                read_start = args.offset if args.offset is not None else 0
                length = args.length if args.length is not None else file_size

                hexdump(fh.read(length), offset=read_start, collapse=args.collapse, color=args.color)
    except KeyboardInterrupt:
        # Caught interrupt; explicit pass
        pass

    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        raise SystemError(f"Caught exception in main:{linesep}{e}")

"""
Contains the functionality for creating hexdump lines from input data.
"""
from os import linesep, environ
from typing import Union, ByteString, Iterator
try:
    import colorama

    colorama.init(autoreset=True)  # Only needed for Windows
except ImportError:
    colorama = None

COLOR_ALWAYS = bool(environ.get('HD2_EN_CLR', False))


def color_always(enable: bool = True):
    """Allows user to set flag to enable always coloring output
    :param enable: Always enable color
    """
    global COLOR_ALWAYS  # pylint: disable=global-statement
    COLOR_ALWAYS = enable


def _line_gen(
    data: ByteString, offset: int = 0x0, collapse: bool = True, color: bool = False
) -> Iterator[str]:
    """Generator function that yields a line.

    :param data: input data, must be bytes-like
    :param offset: offset for address
    :param collapse: flag to turn on/off collapsing multiple same lines
    :param color: enable color output; should only be used when outputting to stdout
    :return:
    """
    # Set color; colorama will import as None if not installed.
    if color and colorama:
        # address area
        address_color = colorama.Fore.GREEN
        # hex and ascii area
        zero_hex_color = colorama.Fore.RESET
        printable_color = colorama.Fore.YELLOW
        non_printable = colorama.Fore.CYAN
        # others
        star_line_color = colorama.Fore.RED

        # Cannot be set
        reset_color = colorama.Fore.RESET

    else:
        star_line_color = ""
        zero_hex_color = ""
        printable_color = ""
        non_printable = ""
        reset_color = ""
        address_color = ""

    # Empty data begets empty line
    if len(data) == 0:
        if offset:
            # Manifests when we've read past the end of a file, which results in an empty buffer.
            # However, the offset we're reading at is still there.  Show the end address in this case.
            # e.g., $ hexdump -s 10m 8mib_file.bin
            # 0800000
            yield f"{address_color}{offset:08x}{linesep}"

        # Return; this will cause a StopIteration
        return

    # Some sequences don't slice nicely (e.g. array.array('I', bytes(16));
    # test if we should convert to bytes
    if isinstance(data, (bytes, bytearray)):
        convert_to_bytes = False
    else:
        convert_to_bytes = True

    def _lookahead_gen():
        last_line_data = None
        yield_star = True

        for i in range(0, len(data), 16):
            line_data = data[i:i+16]
            if collapse and line_data == last_line_data:
                # Only show the star once
                if yield_star:
                    yield_star = False
                    yield f"{star_line_color}*{linesep}"
                else:
                    # Otherwise, just goto the next data
                    continue
            else:
                if convert_to_bytes:
                    if isinstance(line_data, str):
                        # Use the `iso-8859-1` or `latin-1` encodings to map 0x00 to 0xff to bytes 0x00 to 0xff.
                        # c.f. https://docs.python.org/3/library/codecs.html#encodings-and-unicode
                        line_data = bytes(line_data, encoding='iso-8859-1')
                    else:
                        line_data = bytes(line_data)

                # address
                address_value = i + offset

                hex_str = ""
                ascii_str = ""
                hex_str_pad = 50  # 3 chr per position + 2 end spacing
                for j, byte in enumerate(line_data):
                    if byte == 0:
                        character_color = zero_hex_color
                        ascii_chr = "."

                    elif 0x20 <= byte <= 0x7E:
                        character_color = printable_color
                        ascii_chr = chr(byte)

                    else:
                        character_color = non_printable
                        ascii_chr = "."

                    ascii_str += f"{character_color}{ascii_chr}"
                    # Add double spaces after 8 bytes
                    if j != 7:
                        hex_str += f"{character_color}{byte:02x} "
                    else:
                        hex_str += f"{character_color}{byte:02x}  "

                    # Account for padding in color mode
                    hex_str_pad += len(character_color)

                yield_star = True
                yield f"{address_color}{address_value:08x}  " \
                      f"{hex_str: <{hex_str_pad}}" \
                      f"{reset_color}|{ascii_str}{reset_color}|{linesep}"

            last_line_data = line_data

    # Create a lookahead generator, this supports finding the last line, which we might need
    # to print the last address
    gen = _lookahead_gen()
    last = next(gen)
    for line in gen:
        yield last
        last = line

    yield last
    # The last line; assume that receiver is using a function that will add a line seperator.
    yield f"{address_color}{len(data) + offset:08x}{reset_color}"


def hexdump(
    data: Union[ByteString, range],
    result: str = "print",
    offset: int = 0x0,
    collapse: bool = True,
    color: bool = False,
) -> Union[None, str, Iterator[str]]:
    """Function that'll create `hexdump -C` of input data.

    :param data: bytes-like data to hexdump
    :param result: type of output/return, must be `print` (default), `return`, `generator`.
    :param offset: value to add to the address line.
    :param collapse: flag to turn on/off collapsing multiple same lines
    :param color: enable color output; should only be used for outputting to stdout (e.g. `result=print`).
    :return:
    """
    if COLOR_ALWAYS:
        color = COLOR_ALWAYS

    gen = _line_gen(data, offset, collapse, color)
    if result == "print":
        for line in gen:
            print(line, end="")

        # Add newline for last item
        print("")

    elif result == "return":
        return "".join(gen)

    elif result == "generator":
        return gen

    else:
        raise ValueError(
            "`result` argument should be `print`, `return`, or `generator`"
        )


# noinspection PyPep8Naming
class hd:
    """An attempt to get away from the `result` arg by caching the eventual string result.

    Calling this class in an interactive interpreter will cause the generator to be run and printed.
    Calling this within a string will also cause the generator to be run.
    Finally, the end user can use the class as a generator as the __next__ function exists.
    """

    # noinspection PyUnusedLocal
    def __init__(
        self,
        data: ByteString,
        result: str = None,  # pylint: disable=unused-argument
        offset: int = 0x0,
        collapse: bool = True,
    ):
        self._result = "".join(_line_gen(data, offset, collapse))
        self._result_lines = None
        self._line_pos = 0

    def __repr__(self):
        return self._result

    def __iter__(self):
        return self

    def __next__(self):
        if self._result_lines is None:
            # It's an expensive operation, delay until necessary
            self._result_lines = self._result.splitlines()

        try:
            line = self._result_lines[self._line_pos]
            self._line_pos += 1
        except IndexError as e:
            # Allows for re-running the generator
            self._line_pos = 0
            raise StopIteration from e
        return line

"""
Contains the functionality for creating hexdump lines from input data.
"""
from os import environ, linesep, name as os_name
from typing import ByteString, Generator, Iterator, Literal, Union

try:
    import colorama

    if os_name == "nt":
        colorama.init(autoreset=True)  # Only needed for Windows
except ImportError:
    colorama = None

COLOR_ALWAYS = bool(environ.get("HD2_EN_CLR", False))


def color_always(enable: bool = True):
    """Allows user to set flag to enable always coloring output
    :param enable: Always enable color
    """
    global COLOR_ALWAYS  # pylint: disable=global-statement

    # Support http://no-color.org/
    no_color = bool(environ.get("NO_COLOR", False))
    # Token check for color support
    dumb_terminal = environ.get("TERM")
    if no_color or dumb_terminal == "dumb":
        COLOR_ALWAYS = False
    else:
        COLOR_ALWAYS = enable


_non_color_map_ascii = {
    **{_: "." for _ in range(0x20)},
    **{_: chr(_) for _ in range(0x20, 0x7F)},
    **{_: "." for _ in range(0x7F, 0x100)},
}
_non_color_map_hex_str = {
    **{_: f"{_:02x} " for _ in range(0x20)},
    **{_: f"{_:02x} " for _ in range(0x20, 0x7F)},
    **{_: f"{_:02x} " for _ in range(0x7F, 0x100)},
}
if colorama:
    _color_map_ascii = {
        **{0: colorama.Fore.RESET + "."},
        **{_: colorama.Fore.CYAN + "." for _ in range(1, 0x20)},
        **{_: colorama.Fore.YELLOW + chr(_) for _ in range(0x20, 0x7F)},
        **{_: colorama.Fore.CYAN + "." for _ in range(0x7F, 0x100)},
    }
    _color_map_hex_str = {
        **{0: f"{colorama.Fore.RESET}{0:02x} "},
        **{_: f"{colorama.Fore.CYAN}{_:02x} " for _ in range(1, 0x20)},
        **{_: f"{colorama.Fore.YELLOW}{_:02x} " for _ in range(0x20, 0x7F)},
        **{_: f"{colorama.Fore.CYAN}{_:02x} " for _ in range(0x7F, 0x100)},
    }
else:
    _color_map_ascii = _non_color_map_ascii
    _color_map_hex_str = _non_color_map_hex_str

# Used to do a translation on input bytes to what we want printed.
_ascii_str_map = (
    b"................................ !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^"
    b"_`abcdefghijklmnopqrstuvwxyz{|}~.................................................................."
    b"..............................................................."
)


def _line_gen(
    data: ByteString, offset: int = 0x0, collapse: bool = True, color: bool = False
) -> Generator[str, None, None]:
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
        addr_color = colorama.Fore.GREEN
        # others
        star_line_color = colorama.Fore.RED

        # Cannot be set
        reset_color = colorama.Fore.RESET

        # hex and ascii area
        char_map_ascii = _color_map_ascii
        char_map_hex_str = _color_map_hex_str

    else:
        star_line_color = ""
        reset_color = ""
        addr_color = ""
        char_map_ascii = _non_color_map_ascii
        char_map_hex_str = _non_color_map_hex_str

    # Empty data begets empty line
    if len(data) == 0:
        if offset:
            # Manifests when we've read past the end of a file, which results in an empty buffer.
            # However, the offset we're reading at is still there.  Show the end address in this case.
            # e.g., $ hexdump -s 10m 8mib_file.bin
            # 0800000
            yield f"{addr_color}{offset:08x}{linesep}"

        # Return; this will cause a StopIteration
        return

    # Some sequences don't slice nicely (e.g. array.array('I', bytes(16));
    # test if we should convert to bytes
    if not isinstance(data, (bytes, bytearray)):
        if isinstance(data, str):
            # Use the `iso-8859-1` or `latin-1` encodings to map 0x00 to 0xff to bytes
            # 0x00 to 0xff.
            # c.f. https://docs.python.org/3/library/codecs.html#encodings-and-unicode
            data = bytes(data, encoding="iso-8859-1")
        else:
            data = bytes(data)

    last_line_data = None
    yield_star = True
    for addr in range(0, len(data), 16):
        line_data = data[addr : addr + 16]
        if collapse and line_data == last_line_data:
            # Only show the star once
            if yield_star:
                yield_star = False
                yield f"{star_line_color}*{linesep}"
            else:
                # Otherwise, just goto the next data
                continue
        else:
            if color:
                # 8 octets * (2 per + 1 space) + 1 spaces at the end = 25, up to 8 octets * (5 color per) = 40
                first_pad = 25 + min(len(line_data) * 5, 40)
                second_pad = 25 + min(max(0, len(line_data) - 8) * 5, 40)
                # Need to decode first as the translate() method for bytes does not allow a one-to-many mapping
                yield f"{addr_color}{addr + offset:08x}  {line_data[:8].decode(encoding='iso-8859-1').translate(char_map_hex_str): <{first_pad}}{line_data[8:].decode(encoding='iso-8859-1').translate(char_map_hex_str): <{second_pad}}{reset_color}|{line_data.decode(encoding='iso-8859-1').translate(char_map_ascii)}{reset_color}|{linesep}"
            else:
                # Provides a modest speed-up vs using .join()
                yield f"{addr+offset:08x}  {line_data[:8].hex(' '): <25}{line_data[8:].hex(' '): <25}|{line_data.translate(_ascii_str_map).decode('ascii')}|{linesep}"

            yield_star = True

        last_line_data = line_data

    # The last line; assume that receiver is using a function that will add a line seperator.
    yield f"{addr_color}{len(data) + offset:08x}{reset_color}"


def hexdump(
    data: Union[ByteString, range],
    result: Literal["print", "return", "generator"] = "print",
    offset: int = 0x0,
    collapse: bool = True,
    color: bool = False,
) -> Union[None, str, Iterator[str]]:
    """Function that'll create `hexdump -C` of input data.

    :param data: bytes-like data to hexdump
    :param result: type of output/return, must be `print` (default), `return`, `generator`.
    :param offset: value to add to the address line.
    :param collapse: flag to turn on/off collapsing multiple same lines
    :param color: enable color output; should only be used for outputting to stdout
        (e.g. `result=print`).
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
        return None

    if result == "return":
        return "".join(gen)

    if result == "generator":
        return gen

    raise ValueError("`result` argument should be `print`, `return`, or `generator`")


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
        except IndexError as exp_index:
            # Allows for re-running the generator
            self._line_pos = 0
            raise StopIteration from exp_index
        return line

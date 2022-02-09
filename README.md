# Hexdump2

An imperfect replica of `hexdump -C`.  API compatible with the [hexdump package's](https://pypi.org/project/hexdump/) hexdump function, with a few extra features.

## Installation

Use `pip`:
```commandline
pip install hexdump2   
```

## Usage

### As Python Library

Import the `hexdump` function from `hexdump2` package and use. By default, `hexdump` will internally output to stdout using the built-in `print` function:

```python
from hexdump2 import hexdump

hexdump(bytes(32))
"""
00000000  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
*
00000020
"""
```

The `hexdump` function has three ways to provide output, selected by the `result` keyword arg:
1. Print to stdout via the built-in print method - `print` (default)
2. Return a string with all the lines; useful for logging - `return`
3. Return a generator - `generator`

Additional functionality by keyword args:
* `offset` - specify an offset for the address. Default: 0
* `collapse` - turn on/off duplicate lines with `*`. Default: true
* `color` - turn on/off ANSI color codes (provided by [colorama](https://pypi.org/project/colorama/) package). Default: false

Color can be en/disabled all the time with by calling `color_always()` in python or by setting the environmental variable `HD2_EN_CLR` before importing.

```python
from hexdump2 import hexdump, color_always
color_always()  # Defaults to True
hexdump(bytes(32))
"""
[32m00000000[39m  [39m00 [39m00 [39m00 [39m00 [39m00 [39m00 [39m00 [39m00  [39m00 [39m00 [39m00 [39m00 [39m00 [39m00 [39m00 [39m00  [39m|[39m.[39m.[39m.[39m.[39m.[39m.[39m.[39m.[39m.[39m.[39m.[39m.[39m.[39m.[39m.[39m.[39m|
[31m*
[32m00000020
"""
# Disable
color_always(False)
```

## Command Line

A simple command line is provided by running the python console script `hexdump2` or `hd2`:

```commandline
hexdump2 -h
```

If not installed via pip, the command line can also be run with:

```commandline
python3 path/to/hexdump2_package -h 
```

Color can be enabled all the time for the command line by setting the environmental variable `HD2_EN_CLR` with any value (internally it's a string, which is converted to a bool):

```commandline
export HD2_EN_CLR="True"
hd2 0x20_nulls.bin
[32m00000000[39m  [39m00 [39m00 [39m00 [39m00 [39m00 [39m00 [39m00 [39m00  [39m00 [39m00 [39m00 [39m00 [39m00 [39m00 [39m00 [39m00  [39m|[39m.[39m.[39m.[39m.[39m.[39m.[39m.[39m.[39m.[39m.[39m.[39m.[39m.[39m.[39m.[39m.[39m|
[31m*
[32m00000020
```

## Usage Examples

Supply an offset:

```python
from hexdump2 import hexdump
   
hexdump(bytes(32), offset=0x100)
"""
00000100  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
*
00000120
"""
```

Return a string for logging:

```python
import logging
from hexdump2 import hexdump

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Example")
logger.setLevel(logging.INFO)

logger.info(
    f"Example data\n"
    f"{hexdump(bytes(32), result='return')}"
)
"""
INFO:Example:Example data
00000000  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
*
00000020
"""
```

Using the generator, where the `*` operator runs the generator into the `print` method to stderr:

```python
import sys
from hexdump2 import hexdump

print(
    *hexdump(range(256), result='generator'),
    file=sys.stderr
)
"""
00000000  00 01 02 03 04 05 06 07  08 09 0a 0b 0c 0d 0e 0f  |................|
00000010  10 11 12 13 14 15 16 17  18 19 1a 1b 1c 1d 1e 1f  |................|
00000020  20 21 22 23 24 25 26 27  28 29 2a 2b 2c 2d 2e 2f  | !"#$%&'()*+,-./|
00000030  30 31 32 33 34 35 36 37  38 39 3a 3b 3c 3d 3e 3f  |0123456789:;<=>?|
00000040  40 41 42 43 44 45 46 47  48 49 4a 4b 4c 4d 4e 4f  |@ABCDEFGHIJKLMNO|
00000050  50 51 52 53 54 55 56 57  58 59 5a 5b 5c 5d 5e 5f  |PQRSTUVWXYZ[\]^_|
00000060  60 61 62 63 64 65 66 67  68 69 6a 6b 6c 6d 6e 6f  |`abcdefghijklmno|
00000070  70 71 72 73 74 75 76 77  78 79 7a 7b 7c 7d 7e 7f  |pqrstuvwxyz{|}~.|
00000080  80 81 82 83 84 85 86 87  88 89 8a 8b 8c 8d 8e 8f  |................|
00000090  90 91 92 93 94 95 96 97  98 99 9a 9b 9c 9d 9e 9f  |................|
000000a0  a0 a1 a2 a3 a4 a5 a6 a7  a8 a9 aa ab ac ad ae af  |................|
000000b0  b0 b1 b2 b3 b4 b5 b6 b7  b8 b9 ba bb bc bd be bf  |................|
000000c0  c0 c1 c2 c3 c4 c5 c6 c7  c8 c9 ca cb cc cd ce cf  |................|
000000d0  d0 d1 d2 d3 d4 d5 d6 d7  d8 d9 da db dc dd de df  |................|
000000e0  e0 e1 e2 e3 e4 e5 e6 e7  e8 e9 ea eb ec ed ee ef  |................|
000000f0  f0 f1 f2 f3 f4 f5 f6 f7  f8 f9 fa fb fc fd fe ff  |................|
"""
```

### Non-Bytes Classes

Internally, hexdump will chunk an object by slicing.  The sliced object should support checking each item as an `int` (e.g., bytes(1)[0] == 0).

```python
import array
from hexdump2 import hexdump

data = array.array('B', bytes(16))
hexdump(data)
"""
00000000  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
"""
```

A class needs to implement `__bytes__`, `__len__`, and `__getitem__` to support hexdump:
```python
from hexdump2 import hexdump

class SomeStruct:
    def __init__(self, data: bytes):
        self._data = data
        
    def __bytes__(self):
        return self._data
    
    def __len__(self):
        return len(self._data)
    
    def __getitem__(self, item):
        return self._data.__getitem__(item)

some_struct = SomeStruct(bytes(32))
hexdump(some_struct)
"""
00000000  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
*
00000020
"""
```
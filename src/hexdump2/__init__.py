"""
mirrors functionality of hexdump(1) and API interface of Python hexdump package.

Usage:
1. Within Python:
from hexdump2 import hexdump, color_always

# Enable or disable color all the time
color_always()

hexdump(bytes-like data)

2. From commandline, run the console scripts hexdump2 or hd2
$ hd2 -h
"""

# Import for everyone to use
from .hexdump2 import hexdump, hd, color_always

__all__ = ["hexdump", "hd", "color_always"]

import os as __os__

# Import for everyone to use
from .hexdump2 import hexdump, hd

# Use double-underscores to hide these from auto-complete imports
__parent_dir__ = __os__.path.abspath(__os__.path.join(__file__, __os__.pardir))
with open(__os__.path.join(__parent_dir__, "VERSION")) as __version_file__:
    __version__ = __version_file__.read().strip()

__all__ = ["hexdump", "hd", __version__]

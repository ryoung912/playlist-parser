"""Shared source loading for playlist formats.

M3U and PLS both need to treat a file path, "-", None, and an already
open stream the same way, so that logic lives here instead of being
duplicated per format.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import IO, Union

PathLike = Union[str, Path]
Source = Union[PathLike, IO[str], None]


def read_source(source: Source) -> str:
    """Read playlist text from a path, stdin, or an open text stream."""
    if source is None or source == "-":
        return sys.stdin.read()

    if isinstance(source, (str, Path)):
        with open(source, "r", encoding="utf-8") as f:
            return f.read()

    return source.read()

"""Parse and write M3U/M3U8 and PLS audio playlists."""

from . import pls
from .m3u import Track, dumps, load, parse

__all__ = ["Track", "dumps", "load", "parse", "pls"]

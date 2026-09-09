"""M3U / M3U8 playlist parsing.

Format reference: a plain M3U is just one path or URL per line. The
"extended" variant adds a leading #EXTM3U marker and, before each entry,
an optional #EXTINF:<seconds>,<title> line. Both variants show up in the
wild interchangeably (Winamp-era exports lack #EXTM3U entirely), so the
parser does not require the header and treats #EXTINF as optional
metadata rather than something to validate against.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import IO, Iterable, Optional, Union

PathLike = Union[str, Path]
Source = Union[PathLike, IO[str], None]


@dataclass
class Track:
    path: str
    title: Optional[str] = None
    duration: Optional[int] = None  # seconds; -1 in the source means unknown


def parse(text: str) -> list[Track]:
    """Parse M3U/M3U8 content already held in memory."""
    tracks: list[Track] = []
    pending_title: Optional[str] = None
    pending_duration: Optional[int] = None

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        if line.startswith("#EXTINF:"):
            payload = line[len("#EXTINF:"):]
            duration_str, _, title = payload.partition(",")
            try:
                duration = int(duration_str.strip())
            except ValueError:
                duration = None
            pending_duration = None if duration == -1 else duration
            pending_title = title.strip() or None
            continue

        if line.startswith("#"):
            # Other directives (#EXTM3U, #EXT-X-*, comments) carry no
            # track data we can use, so skip them.
            continue

        tracks.append(Track(path=line, title=pending_title, duration=pending_duration))
        pending_title = None
        pending_duration = None

    return tracks


def load(source: Source = None) -> list[Track]:
    """Load a playlist from a path, an open text stream, or stdin.

    - A string or Path is opened and read as a file.
    - The string "-" and the value None both mean "read stdin", so
      callers can wire up an optional path argument without a branch.
    - Anything else is assumed to already be an open text stream (a
      file object, io.StringIO, sys.stdin, ...) and is read directly.
    """
    if source is None or source == "-":
        return parse(sys.stdin.read())

    if isinstance(source, (str, Path)):
        with open(source, "r", encoding="utf-8") as f:
            return parse(f.read())

    return parse(source.read())


def dumps(tracks: Iterable[Track]) -> str:
    """Render tracks back into extended M3U8 text."""
    lines = ["#EXTM3U"]
    for track in tracks:
        if track.title is not None or track.duration is not None:
            duration = track.duration if track.duration is not None else -1
            lines.append(f"#EXTINF:{duration},{track.title or ''}")
        lines.append(track.path)
    return "\n".join(lines) + "\n"

"""PLS playlist parsing.

PLS is an INI-style format: a [playlist] section with FileN/TitleN/LengthN
lines keyed by a 1-based index, plus a NumberOfEntries/Version footer.
Players don't guarantee the three lines for a given index are adjacent or
in order, so entries are collected into per-field dicts keyed by index
and only assembled into Track objects once the whole file has been read.
"""

from __future__ import annotations

from typing import Iterable, Optional

from ._io import Source, read_source
from .m3u import Track


def _index_suffix(key: str, prefix: str) -> Optional[int]:
    suffix = key[len(prefix):]
    return int(suffix) if suffix.isdigit() else None


def parse(text: str) -> list[Track]:
    """Parse PLS content already held in memory."""
    paths: dict[int, str] = {}
    titles: dict[int, str] = {}
    durations: dict[int, Optional[int]] = {}

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith(";") or line.startswith("["):
            continue

        key, sep, value = line.partition("=")
        if not sep:
            continue
        key = key.strip().lower()
        value = value.strip()

        if key.startswith("file"):
            index = _index_suffix(key, "file")
            if index is not None:
                paths[index] = value
        elif key.startswith("title"):
            index = _index_suffix(key, "title")
            if index is not None:
                titles[index] = value
        elif key.startswith("length"):
            index = _index_suffix(key, "length")
            if index is not None:
                try:
                    length = int(value)
                except ValueError:
                    continue
                durations[index] = None if length < 0 else length

    return [
        Track(path=paths[index], title=titles.get(index) or None, duration=durations.get(index))
        for index in sorted(paths)
    ]


def load(source: Source = None) -> list[Track]:
    """Load a PLS playlist from a path, an open text stream, or stdin.

    Follows the same source-handling rules as `playlists.m3u.load`.
    """
    return parse(read_source(source))


def dumps(tracks: Iterable[Track]) -> str:
    """Render tracks back into PLS text."""
    tracks = list(tracks)
    lines = ["[playlist]"]
    for i, track in enumerate(tracks, start=1):
        lines.append(f"File{i}={track.path}")
        lines.append(f"Title{i}={track.title or ''}")
        duration = track.duration if track.duration is not None else -1
        lines.append(f"Length{i}={duration}")
    lines.append(f"NumberOfEntries={len(tracks)}")
    lines.append("Version=2")
    return "\n".join(lines) + "\n"

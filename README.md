# playlists

A small library for reading and writing M3U/M3U8 and PLS audio playlists.

Every media player writes M3U slightly differently: some skip the
`#EXTM3U` header, some skip `#EXTINF` duration/title metadata entirely,
some use absolute paths and some use URLs. This library parses the
format defensively and gives you a plain list of `Track` objects instead
of an object graph you have to inspect just to get a file path back out.

The other thing it gets right: playlists frequently arrive over a pipe
(exported from a script, piped from `curl`, generated on the fly) rather
than sitting on disk as a named file. `playlists.load()` handles a file
path, `-`, `None`, or an already-open stream identically, so a caller
doesn't need a separate code path for "reading from stdin."

## Install

No PyPI release yet. Copy `src/playlists` into your project, or add this
repo as a path dependency.

## Usage

```python
import playlists

# from a file path
tracks = playlists.load("my_mix.m3u8")

# from stdin (both of these are equivalent)
tracks = playlists.load()
tracks = playlists.load("-")

for t in tracks:
    print(t.path, t.title, t.duration)
```

Parsing text you already have in memory:

```python
import playlists

text = """#EXTM3U
#EXTINF:213,Boards of Canada - Roygbiv
music/roygbiv.flac
#EXTINF:-1,Untitled Track
music/side_b/03.mp3
"""

tracks = playlists.parse(text)
# [Track(path='music/roygbiv.flac', title='Boards of Canada - Roygbiv', duration=213),
#  Track(path='music/side_b/03.mp3', title='Untitled Track', duration=None)]
```

Writing a playlist back out:

```python
import playlists

playlist_text = playlists.dumps(tracks)
```

Reading from a pipe on the command line, with your own thin script:

```sh
cat my_mix.m3u8 | python -c "import playlists, sys; print(len(playlists.load(sys.stdin)))"
```

PLS playlists use the same `Track` type, under `playlists.pls`:

```python
import playlists.pls

tracks = playlists.pls.load("my_mix.pls")
playlist_text = playlists.pls.dumps(tracks)
```

## Status

Early. M3U/M3U8 and PLS read and write both work. See the roadmap in
commit history for what's planned next (unit tests, relative-path
resolution, malformed input handling).

## License

MIT, see LICENSE.

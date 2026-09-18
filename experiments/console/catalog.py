"""Validated cartridge manifests and desktop-space insertion geometry."""
import json
import math
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
ACCENTS = {'cyan', 'orange', 'blue', 'bright_green', 'red', 'yellow', 'green'}


def load_games(root=ROOT):
    """Load bundled games, then games/*/game.json; never execute discovery code."""
    root = Path(root).resolve()
    bundled = root / 'experiments/console/games.json'
    entries = [(bundled, entry, root) for entry in json.loads(bundled.read_text())]
    for manifest in sorted((root / 'games').glob('*/game.json')):
        entries.append((manifest, json.loads(manifest.read_text()), manifest.parent))
    games = []
    ids = set()
    for manifest, entry, base in entries:
        def fail(message):
            raise ValueError(f'{manifest}: {message}')
        if not isinstance(entry, dict):
            fail('each cartridge must be an object')
        for key in ('id', 'title', 'subtitle', 'accent', 'entry'):
            if not isinstance(entry.get(key), str) or not entry[key].strip():
                fail(f'{key} must be a nonempty string')
        ident = entry['id']
        if not re.fullmatch(r'[a-z][a-z0-9-]{0,31}', ident) or ident == 'console':
            fail('id must be a lowercase slug, at most 32 characters, other than console')
        if ident in ids:
            fail(f'duplicate id: {ident}')
        if len(entry['title']) > 20 or len(entry['subtitle']) > 48:
            fail('title is limited to 20 characters; subtitle to 48')
        if entry['accent'] not in ACCENTS:
            fail(f'accent must be one of {sorted(ACCENTS)}')
        script = (base / entry['entry']).resolve()
        if not script.is_relative_to(root) or script.suffix != '.py' or not script.is_file():
            fail('entry must point to an existing Python file inside the repository')
        ids.add(ident)
        games.append(dict(entry, number=f'{len(games)+1:02}',
                          command=[sys.executable, str(script)]))
    return tuple(games)


GAMES = load_games()
CONSOLE = (560, 360)
CARTRIDGE = (210, 250)


def starting_layout(monitor, games=GAMES):
    """Fit additional cartridges in rows without placing them off the monitor."""
    x, y, width, height = monitor
    base = min(1., width / 1200, height / 820)
    columns = min(len(games), max(1, int(width / (240 * base))))
    rows = math.ceil(len(games) / columns)
    scale = min(base, height * .48 / (rows * 270))
    cx, cy = x + width / 2, y + height * .74
    result = {'console': (int(cx-280*scale), int(cy-180*scale),
                          int(560*scale), int(360*scale))}
    for i, game in enumerate(games):
        row, col = divmod(i, columns)
        count = min(columns, len(games)-row*columns)
        result[game['id']] = (
            int(cx + (col-(count-1)/2)*240*scale - 105*scale),
            int(y + height*.04 + row*270*scale),
            int(210*scale), int(250*scale))
    return result, scale


def aligned(console, cartridge):
    x, y, w, h = console
    cx, cy, cw, ch = cartridge
    return abs(cx+cw/2-(x+w/2)) < w*.16 and abs(cy+ch-(y+h*.32)) < h*.11

#!/usr/bin/env python3
"""Create a cartridge from the two-window docking example."""
import argparse
import json
from pathlib import Path
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]


def create_game(slug, title, root=ROOT):
    root = Path(root)
    if not re.fullmatch(r'[a-z][a-z0-9-]{0,31}', slug) or slug == 'console':
        raise ValueError('Choose a lowercase slug (letters, digits, hyphens), at most 32 characters.')
    if not title.strip() or len(title) > 20:
        raise ValueError('Choose a title between 1 and 20 characters.')
    existing = json.loads((root/'experiments/console/games.json').read_text())
    for manifest in (root/'games').glob('*/game.json'):
        existing.append(json.loads(manifest.read_text()))
    if any(g['id'] == slug for g in existing):
        raise ValueError(f'Cartridge id already exists: {slug}')
    destination = root/'games'/slug
    if destination.exists():
        raise ValueError(f'Refusing to overwrite {destination}')
    shutil.copytree(root/'templates/window-game', destination,
                    ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    manifest = dict(id=slug, title=title, subtitle='A COMMUNITY WINDOW GAME',
                    accent='cyan', entry='main.py')
    (destination/'game.json').write_text(json.dumps(manifest, indent=2)+'\n')
    return destination


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('slug')
    parser.add_argument('--title', default='MY WINDOW GAME')
    args = parser.parse_args()
    try:
        destination = create_game(args.slug, args.title)
    except ValueError as error:
        parser.error(str(error))
    print(f'Created {destination}\nRelaunch ./arcade to find your cartridge.')


if __name__ == '__main__':
    main()

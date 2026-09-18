#!/usr/bin/env python3
"""Run suites in separate processes so game-local model/art imports cannot collide."""
import argparse
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
CORE = ('.', 'tools', 'experiments/console', 'experiments/quattro-jump',
        'experiments/lemur-falls', 'experiments/omarchy-wars', 'templates/window-game')
LABS = ('experiments/platform-lab', 'experiments/window-lab')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--labs', action='store_true', help='Also test older window/platform labs')
    args = parser.parse_args()
    suites = list(CORE) + [str(p.relative_to(ROOT)) for p in sorted((ROOT/'games').glob('*'))
                          if p.is_dir() and list(p.glob('test_*.py'))]
    if args.labs:
        suites.extend(LABS)
    failures = []
    for suite in suites:
        print(f'\n=== {suite} ===', flush=True)
        result = subprocess.run(
            [sys.executable, '-m', 'unittest', 'discover', '-s', suite, '-p', 'test_*.py'],
            cwd=ROOT, env={**os.environ, 'GDK_BACKEND': 'wayland'})
        if result.returncode:
            failures.append(suite)
    print('\nFailed: '+', '.join(failures) if failures else '\nAll suites passed.')
    return bool(failures)


if __name__ == '__main__':
    sys.exit(main())

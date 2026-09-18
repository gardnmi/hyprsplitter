#!/usr/bin/env python3
"""Cross three demo endings without opening windows or altering game recordings."""
import os
from pathlib import Path
import subprocess
import tempfile

from run import build


def main():
    source = Path.home() / 'Projects/terminal-doom'
    with tempfile.TemporaryDirectory(prefix='pixel-doom-loop-test-') as directory:
        root = Path(directory)
        binary = root / 'bridge-fast-test'
        build(source, binary, ['-DPIXEL_DOOM_TEST_FAST'])
        frame = root / 'frame.rgb'
        frame.write_bytes(bytes(320 * 200 * 3))
        result = subprocess.run(
            [str(binary), str(frame), '320', '200', '-iwad', str(source / 'doom1.wad'),
             '-config', str(root / 'doom.cfg'), '-nosound', '-playdemo', 'demo1'],
            cwd=root, env=dict(os.environ, PIXEL_DOOM_LOOP_DEMO='1', PIXEL_DOOM_OUTPUT_FPS='35'),
            stdin=subprocess.DEVNULL, capture_output=True, timeout=60,
        )
        assert result.returncode == 0, result.stderr.decode(errors='replace')[-2000:]
        assert b'LOOP_TEST_PASSED: 18000 game ticks in one process' in result.stderr
        print('PASS: one engine survived 18,000 ticks and three demo endings')


if __name__ == '__main__':
    main()

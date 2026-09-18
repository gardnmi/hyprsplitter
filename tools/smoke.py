#!/usr/bin/env python3
"""LIVE desktop test: briefly open each bundled game and starter, then send SIGTERM."""
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from hyprsplitter import Hyprland

ENTRIES = (
    'experiments/console/main.py',
    'hyprsplitter.py',
    'experiments/quattro-jump/main.py',
    'experiments/lemur-falls/main.py',
    'experiments/omarchy-wars/main.py',
    'templates/window-game/main.py',
)


def main():
    hypr = Hyprland()
    failed = []
    for entry in ENTRIES:
        print(f'Opening {entry}', flush=True)
        before = hypr.request('activeworkspace', True)['name']
        with tempfile.TemporaryFile(mode='w+') as log:
            process = subprocess.Popen(
                [sys.executable, str(ROOT/entry)], cwd=ROOT,
                env={**os.environ, 'GDK_BACKEND':'wayland'},
                stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
            problem = None
            try:
                time.sleep(4)
                if process.poll() is not None:
                    problem = 'exited during startup'
                clients = hypr.request('clients', True)
                if not any(c.get('pid') == process.pid for c in clients):
                    problem = problem or 'no native windows mapped'
            finally:
                if process.poll() is None:
                    process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait()
                    problem = 'shutdown timed out'
            if process.returncode != 0:
                problem = problem or f'exit code {process.returncode}'
            if any(c.get('pid') == process.pid for c in hypr.request('clients', True)):
                problem = problem or 'owned windows remained after exit'
            if hypr.request('activeworkspace', True)['name'] != before:
                problem = problem or 'previous workspace was not restored'
            log.seek(0)
            output = log.read()
            if 'Traceback (most recent call last)' in output:
                problem = problem or 'Python traceback during startup/drawing'
            if problem:
                failed.append(entry)
                print(f'FAIL: {problem}\n{output}', flush=True)
            else:
                print('PASS: mapped windows, clean exit, restored workspace', flush=True)
    return bool(failed)


if __name__ == '__main__':
    sys.exit(main())

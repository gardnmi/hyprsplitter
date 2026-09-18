#!/usr/bin/env python3
"""Read-only dependency checks; does not open windows or change desktop settings."""
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
failures = []


def check(label, okay, hint):
    print(f'{"OK" if okay else "MISSING"}  {label}')
    if not okay:
        failures.append(label)
        print(f'         {hint}')


def python_check(code):
    return subprocess.run([sys.executable, '-c', code], stdout=subprocess.DEVNULL,
                          stderr=subprocess.DEVNULL).returncode == 0


def main():
    check('Python 3.11+', sys.version_info >= (3,11), 'Use Omarchy system Python: /usr/bin/python')
    check('GTK3 + Cairo', python_check("import gi,cairo; gi.require_version('Gtk','3.0'); from gi.repository import Gtk"),
          'Install python-gobject python-cairo gtk3')
    check('GTK4 layer shell (Road to OMACON)', python_check(
        "from ctypes import CDLL; CDLL('libgtk4-layer-shell.so'); import gi; "
        "gi.require_version('Gtk','4.0'); gi.require_version('Gtk4LayerShell','1.0'); "
        "from gi.repository import Gtk,Gtk4LayerShell"),
        'Install gtk4 gtk4-layer-shell')
    check('ttfx (Road to OMACON)', shutil.which('ttfx') is not None, 'Install ttfx')
    check('Wayland session', bool(os.environ.get('WAYLAND_DISPLAY')), 'Run from a terminal in your Omarchy desktop')
    try:
        from hyprsplitter import Hyprland
        h = Hyprland()
        h.request('monitors', True)
        h.request('eval assert(type(hl.window_rule) == "function" and type(hl.dsp.focus) == "function")')
        check('Hyprland Lua IPC', True, '')
        for option, field, expected in (
            ('general:layout','str','dwindle'),
            ('dwindle:preserve_split','bool',True),
            ('dwindle:use_active_for_splits','bool',True)):
            check(option+' (Flight School)', h.request('getoption '+option,True).get(field) == expected,
                  'Flight School requires dwindle with preserve_split and use_active_for_splits')
    except Exception as error:
        check('Hyprland Lua IPC', False, str(error))
    sys.path.insert(0, str(ROOT/'experiments/console'))
    try:
        from catalog import load_games
        games = load_games()
        check(f'{len(games)} cartridge manifests', True, '')
    except (OSError, ValueError) as error:
        check('Cartridge manifests', False, str(error))
    print('\nChecks failed: '+', '.join(failures) if failures else '\nReady for the bundled collection.')
    return bool(failures)


if __name__ == '__main__':
    sys.exit(main())

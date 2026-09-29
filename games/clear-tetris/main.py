#!/usr/bin/env python3
"""A transparent, floating Tetris board on the current Hyprland workspace."""
import json
import os
from pathlib import Path
import signal
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
gi.require_version('GLibUnix', '2.0')
from gi.repository import Gtk, Gdk, GLib, GLibUnix

from hyprsplitter import Hyprland
from model import Game
# The repository also has a render.py; prefer this cartridge's module.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from render import draw, WINDOW_W, WINDOW_H


class App:
    def __init__(self):
        self.closed = False
        self.error = None
        self.window = None
        self.rule = None
        self.timers = []
        self.hypr = Hyprland()
        self.game = Game()
        self.paused = True
        self.focused = False
        self.visible = True
        self.tint_index = 0
        self.grid = True
        self.pressed = set()
        self.direction = 0
        self.repeat_at = 0.
        self.placed = False
        self.last = time.monotonic()
        self.deadline = self.last + 5
        try:
            self.setup()
        except Exception:
            self.close()
            raise

    def setup(self):
        self.title = f'ClearTetris-{os.getpid()}'
        self.rule = f'clear_tetris_{os.getpid()}'
        self.hypr.request(
            f'eval {self.rule}=hl.window_rule({{name="{self.rule}",'
            f'match={{initial_title="^{self.title}$"}},float=true,no_anim=true,'
            'rounding=0,border_size=0,no_shadow=true,no_blur=true,'
            'opacity="1 override 1 override"})')
        monitor = next(m for m in self.hypr.request('monitors', True) if m['focused'])
        mw, mh = monitor['width'], monitor['height']
        if monitor.get('transform', 0) % 2:
            mw, mh = mh, mw
        width, height = mw / monitor['scale'], mh / monitor['scale']
        left, top, right, bottom = monitor.get('reserved', [0, 0, 0, 0])
        self.scale = min(1., (height - top - bottom - 40) / WINDOW_H,
                         (width - left - right - 40) / WINDOW_W)
        self.size = (int(WINDOW_W * self.scale), int(WINDOW_H * self.scale))
        self.position = (int(monitor['x'] + width - right - self.size[0] - 20),
                         int(monitor['y'] + top + 20))
        self.window = Gtk.Window(title=self.title)
        self.window.set_default_size(*self.size)
        self.window.set_decorated(False)
        self.window.set_resizable(False)
        self.window.set_app_paintable(True)
        self.window.set_keep_above(True)
        self.window.set_focus_on_map(False)
        visual = self.window.get_screen().get_rgba_visual()
        if visual is None:
            raise RuntimeError('An RGBA-capable desktop is required for transparency.')
        self.window.set_visual(visual)
        css = Gtk.CssProvider()
        css.load_from_data(b'window, drawingarea { background-color: transparent; }')
        self.window.get_style_context().add_provider(css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self.window.connect('delete-event', lambda *_: self.close() or True)
        self.window.connect('key-press-event', self.key, True)
        self.window.connect('key-release-event', self.key, False)
        self.window.connect('focus-in-event', self.focus, True)
        self.window.connect('focus-out-event', self.focus, False)
        self.area = Gtk.DrawingArea()
        self.area.get_style_context().add_provider(css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self.area.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.area.connect('button-press-event', self.click)
        self.area.connect('draw', self.draw)
        self.window.add(self.area)
        self.window.show_all()
        self.timers.append(GLib.timeout_add(16, lambda: self.guard(self.tick)))
        self.timers.append(GLib.timeout_add(250, lambda: self.guard(self.sync)))
        for sig in (signal.SIGTERM, signal.SIGINT):
            self.timers.append(GLibUnix.signal_add(GLib.PRIORITY_DEFAULT, sig, self.close))

    def guard(self, callback):
        try:
            return callback()
        except Exception as error:
            self.error = str(error)
            print(f'Clear Tetris: {error}', file=sys.stderr, flush=True)
            self.close()
            return False

    def sync(self):
        clients = self.hypr.request('clients', True)
        client = next((c for c in clients if c.get('initialTitle') == self.title), None)
        if client is None:
            if self.placed or time.monotonic() > self.deadline:
                raise RuntimeError('Game window disappeared or failed to map.')
            return True
        if not self.placed:
            selector = json.dumps('address:' + client['address'])
            self.hypr.run(
                f'hl.dsp.window.resize({{window={selector},x={self.size[0]},y={self.size[1]}}})',
                f'hl.dsp.window.move({{window={selector},x={self.position[0]},y={self.position[1]}}})')
            self.placed = True
        # Check every monitor, so a board on an unfocused monitor remains visible.
        monitors = self.hypr.request('monitors', True)
        workspace = client['workspace']['id']
        self.visible = any(workspace in (m['activeWorkspace']['id'],
                                        m.get('specialWorkspace', {}).get('id', 0))
                           for m in monitors)
        if not self.visible:
            self.pause()
        return True

    def pause(self):
        self.paused = True
        self.pressed.clear()
        self.direction = 0

    def focus(self, widget, event, focused):
        self.focused = focused
        if not focused:
            self.pause()
        self.area.queue_draw()
        return False

    def toggle_pause(self):
        if not self.game.over:
            if self.paused:
                self.paused = False
                self.last = time.monotonic()
            else:
                self.pause()
        self.area.queue_draw()

    def key(self, widget, event, down):
        key = Gdk.keyval_name(event.keyval).lower()
        if not down:
            self.pressed.discard(key)
            if key in ('left', 'right'):
                self.direction = (-1 if 'left' in self.pressed else
                                  1 if 'right' in self.pressed else 0)
                self.repeat_at = time.monotonic() + .15
            return True
        if key in self.pressed:
            return True
        self.pressed.add(key)
        if key == 'escape':
            self.close()
        elif key in ('p', 'return'):
            self.toggle_pause()
        elif key == 'r':
            self.game = Game()
            self.pause()
        elif key == 't':
            self.tint_index = (self.tint_index + 1) % 4
        elif key == 'g':
            self.grid = not self.grid
        elif not self.paused and not self.game.over:
            if key in ('left', 'right'):
                self.direction = -1 if key == 'left' else 1
                self.game.move(self.direction)
                self.repeat_at = time.monotonic() + .16
            elif key in ('up', 'x', 'z'):
                self.game.rotate(key != 'z')
            elif key == 'space':
                self.game.hard_drop()
            elif key in ('c', 'shift_l', 'shift_r'):
                self.game.hold()
        if not self.closed:
            # Pause/reset clear movement keys, but retain this key until release
            # so native key repeat cannot toggle pause repeatedly.
            self.pressed.add(key)
            self.area.queue_draw()
        return True

    def click(self, area, event):
        if event.button != 1:
            return False
        x = event.x * WINDOW_W / area.get_allocated_width()
        y = event.y * WINDOW_H / area.get_allocated_height()
        if y < 40 and x >= 340:
            self.close()
        elif y < 40 and x >= 306:
            self.toggle_pause()
        elif y < 92:
            self.window.begin_move_drag(1, int(event.x_root), int(event.y_root), event.time)
        elif 32 <= x <= 260 and 318 <= y <= 404 and self.paused:
            self.toggle_pause()
        return True

    def tick(self):
        now = time.monotonic()
        dt, self.last = min(.05, now - self.last), now
        if self.visible and self.focused and not self.paused and not self.game.over:
            if self.direction and now >= self.repeat_at:
                self.game.move(self.direction)
                self.repeat_at = now + .045
            self.game.update(dt, 'down' in self.pressed)
            self.area.queue_draw()
        return True

    def draw(self, area, c):
        c.scale(area.get_allocated_width() / WINDOW_W,
                area.get_allocated_height() / WINDOW_H)
        draw(c, self.game, self.paused, (0., .12, .28, .48)[self.tint_index], self.grid)

    def close(self, *_):
        if self.closed:
            return False
        self.closed = True
        for timer in self.timers:
            GLib.source_remove(timer)
        self.timers.clear()
        if self.window:
            self.window.destroy()
        if self.rule:
            try:
                self.hypr.request(f'eval if {self.rule} then {self.rule}:set_enabled(false); {self.rule}=nil end')
            except Exception as error:
                self.error = str(error)
                print(f'Rule cleanup: {error}', file=sys.stderr)
        if Gtk.main_level():
            Gtk.main_quit()
        return False


if __name__ == '__main__':
    app = App()
    try:
        Gtk.main()
    finally:
        app.close()
    sys.exit(bool(app.error))

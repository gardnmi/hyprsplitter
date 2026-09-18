#!/usr/bin/env python3
"""A small, complete two-window game. Copy with tools/new_game.py."""
import json
import math
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

from experiments.theme import rgb
from hyprsplitter import Hyprland
from model import docked


class App:
    def __init__(self):
        self.closed = False
        self.windows = {}
        self.rule = None
        self.previous = None
        self.workspace = None
        self.hypr = Hyprland()
        try:
            self.setup()
        except Exception:
            self.close()
            raise

    def setup(self):
        self.previous = self.hypr.request('activeworkspace', True)['name']
        used = {w['id'] for w in self.hypr.request('workspaces', True)}
        self.workspace = next(i for i in range(2, 1000) if i not in used)
        self.prefix = f'Omatari-Example-{os.getpid()}'
        self.rule = f'omatari_example_{os.getpid()}'
        self.hypr.request(
            f'eval {self.rule}=hl.window_rule({{name="{self.rule}",'
            f'match={{initial_title="^{self.prefix}-.*$"}},'
            f'workspace="{self.workspace}",float=true,no_anim=true}})')
        self.hypr.run(f'hl.dsp.focus({{workspace="{self.workspace}"}})')
        monitor = next(m for m in self.hypr.request('monitors', True) if m['focused'])
        width, height = monitor['width']/monitor['scale'], monitor['height']/monitor['scale']
        size = int(min(220, width*.20, height*.3))
        x, y = monitor['x'], monitor['y']
        self.starts = {
            'dock': (int(x+width*.56), int(y+height*.35), size*2, size*2),
            'ship': (int(x+width*.16), int(y+height*.4), size, size),
        }
        self.pending = set(self.starts)
        self.placed = set()
        self.won = False
        self.visible = True
        self.clock = 0.
        self.last = time.monotonic()
        self.mapping_deadline = self.last+5
        for role, rect in self.starts.items():
            window = Gtk.Window(title=self.prefix+'-'+role)
            window.set_default_size(*rect[2:])
            window.connect('delete-event', lambda *_: self.close() or True)
            window.connect('key-press-event', self.key)
            area = Gtk.DrawingArea()
            area.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
            area.connect('button-press-event', self.drag, window)
            area.connect('draw', self.draw, role)
            window.add(area)
            self.windows[role] = window
            window.show_all()
        GLib.timeout_add(60, self.sync)
        GLib.timeout_add(33, self.tick)
        for sig in (signal.SIGTERM, signal.SIGINT):
            GLibUnix.signal_add(GLib.PRIORITY_DEFAULT, sig, self.close)

    def sync(self):
        if self.closed:
            return False
        try:
            clients = self.hypr.request('clients', True)
            rectangles = {}
            for role in self.windows:
                client = next((c for c in clients if c.get('initialTitle') == self.prefix+'-'+role), None)
                if client is None:
                    if role in self.placed or time.monotonic() > self.mapping_deadline:
                        self.close()
                        return False
                    continue
                if role in self.pending:
                    x,y,w,h = self.starts[role]
                    selector = json.dumps('address:'+client['address'])
                    self.hypr.run(
                        f'hl.dsp.window.resize({{window={selector},x={w},y={h}}})',
                        f'hl.dsp.window.move({{window={selector},x={x},y={y}}})')
                    self.pending.remove(role)
                    self.placed.add(role)
                    return True
                rectangles[role] = tuple(client['at']+client['size'])
            self.visible = self.hypr.request('activeworkspace', True)['id'] == self.workspace
            if self.visible and len(rectangles) == 2:
                self.won = self.won or docked(rectangles['ship'], rectangles['dock'])
            return True
        except Exception as error:
            print(f'Game: {error}', file=sys.stderr)
            self.close()
            return False

    def tick(self):
        if self.closed:
            return False
        now = time.monotonic()
        dt = min(.05, now-self.last)
        self.last = now
        if self.visible:
            self.clock += dt
            for window in self.windows.values():
                window.queue_draw()
        return True

    def drag(self, area, event, window):
        if event.button == 1:
            window.begin_move_drag(1, int(event.x_root), int(event.y_root), event.time)
        return True

    def key(self, window, event):
        key = Gdk.keyval_name(event.keyval).lower()
        if key == 'escape':
            self.close()
        elif key == 'r':
            self.won = False
            self.pending = set(self.starts)
        return True

    def draw(self, area, context, role):
        width, height = area.get_allocated_width(), area.get_allocated_height()
        context.set_source_rgb(*rgb('background'))
        context.paint()
        context.set_source_rgb(*rgb('bright_green' if self.won else 'cyan'))
        context.set_line_width(3)
        if role == 'ship':
            context.arc(width/2, height/2, min(width,height)*(.17+.02*math.sin(self.clock*3)), 0, math.tau)
        else:
            context.rectangle(12,12,width-24,height-24)
        context.stroke()
        context.select_font_face('monospace',0,0)
        context.set_font_size(12)
        context.move_to(18,30)
        context.show_text('DOCKED! R / RETRY' if self.won else 'DRAG ME' if role == 'ship' else 'DOCK THE SMALL WINDOW HERE')
        context.move_to(18,height-18)
        context.show_text('ESC / EXIT')

    def close(self, *_):
        if self.closed:
            return False
        self.closed = True
        for window in self.windows.values():
            window.destroy()
        if self.rule:
            try:
                self.hypr.request(f'eval if {self.rule} then {self.rule}:set_enabled(false); {self.rule}=nil end')
            except Exception as error:
                print(f'Rule cleanup: {error}', file=sys.stderr)
        if self.previous is not None:
            try:
                if self.hypr.request('activeworkspace', True)['id'] == self.workspace:
                    self.hypr.run(f'hl.dsp.focus({{workspace={json.dumps(self.previous)}}})')
            except Exception as error:
                print(f'Focus cleanup: {error}', file=sys.stderr)
        if Gtk.main_level():
            Gtk.main_quit()
        return False


if __name__ == '__main__':
    app = App()
    try:
        Gtk.main()
    finally:
        app.close()

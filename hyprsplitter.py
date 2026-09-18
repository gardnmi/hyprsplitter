#!/usr/bin/env python3
"""Hyprsplitter: spaceship lessons for real Omarchy window shortcuts."""

import argparse
import json
import os
import signal
import socket
import sys
import time
import traceback

from game import Game, TARGETS, FRIENDLIES
from field import grid_steps, SECTORS, sector
from controls import MISSIONS, shortcut_labels


class Hyprland:
    def __init__(self):
        signature = os.environ.get("HYPRLAND_INSTANCE_SIGNATURE")
        runtime = os.environ.get("XDG_RUNTIME_DIR")
        if not signature or not runtime:
            raise RuntimeError("Run this inside your Hyprland session.")
        self.path = f"{runtime}/hypr/{signature}/.socket.sock"

    def request(self, command, parse=False):
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as connection:
            connection.settimeout(2)
            connection.connect(self.path)
            connection.sendall((("j/" if parse else "/") + command).encode())
            data = bytearray()
            while chunk := connection.recv(65536):
                data.extend(chunk)
        result = data.decode()
        if parse:
            return json.loads(result)
        if result.strip() != "ok":
            raise RuntimeError(f"Hyprland rejected {command}: {result}")
        return result

    def run(self, *actions):
        self.request("eval " + "; ".join(f"hl.dispatch({action})" for action in actions))

    def focus(self, address):
        self.run(f'hl.dsp.focus({{window="address:{address}"}})')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lesson', choices=[m[0] for m in MISSIONS], default='asteroids')
    parser.add_argument('--smoke-test', action='store_true', help='Exercise every mission with real windows, then exit')
    args = parser.parse_args()
    hypr = Hyprland()
    if hypr.request('getoption general:layout', True).get('str') != 'dwindle':
        raise RuntimeError('This teaching prototype requires the dwindle layout.')
    for option in ('preserve_split', 'use_active_for_splits'):
        if not hypr.request('getoption dwindle:'+option, True).get('bool'):
            raise RuntimeError(f'This prototype requires dwindle:{option} enabled.')
    import gi
    gi.require_version('Gtk', '3.0')
    gi.require_version('Gdk', '3.0')
    gi.require_version('GLibUnix', '2.0')
    from gi.repository import Gdk, GLib, GLibUnix, Gtk
    from render import draw_tile

    class App:
        def __init__(self):
            self.game = Game(args.lesson)
            self.game.controls = shortcut_labels(hypr.request('binds', True))
            self.windows, self.addresses, self.geometry = {}, {}, {}
            self.ready = self.closing = self.away = False
            self.error = None
            self.previous = hypr.request('activeworkspace', True)['name']
            self.previous_window = hypr.request('activewindow', True).get('address')
            occupied = {w['id'] for w in hypr.request('workspaces', True)}
            self.workspace = next(i for i in range(90, 10000) if i not in occupied)
            self.prefix = f'Hyprsplitter-{os.getpid()}'
            self.rule = f'hyprsplitter_{os.getpid()}'
            self.rule_installed = False
            self.last_tick = time.monotonic()
            self.last_sync = 0
            self.smoke_stage = 0
            self.smoke_time = 0
            self.generation = 0

        def guarded(self, fn):
            try:
                return fn()
            except Exception as error:
                self.error = f'{type(error).__name__}: {error}'
                traceback.print_exc()
                self.close()
                return False

        def begin(self):
            hypr.request(f'eval {self.rule} = hl.window_rule({{name="{self.rule}", '
                         f'match={{initial_title="^{self.prefix}-.*$"}}, '
                         f'workspace="{self.workspace}", tile=true, '
                         'opacity="1 override 1 override", no_anim=false})')
            self.rule_installed = True
            hypr.run(f'hl.dsp.focus({{workspace="{self.workspace}"}})')
            self.build()
            GLib.timeout_add(33, lambda: self.guarded(self.frame))

        def build(self):
            self.ready = False
            self.generation += 1
            for win in list(self.windows.values()):
                win.destroy()
            self.windows.clear()
            self.addresses.clear()
            self.geometry.clear()
            self.arena = None
            self.dock_prepared = False
            if self.game.mission == 'asteroids':
                steps = grid_steps()
            elif self.game.mission == 'shoot':
                steps = grid_steps(4, 4)
            else:
                steps = [(4,None,None,None),(0,4,'r',1)]
            self.steps = iter(steps)
            self.pending = None
            self.created_at = time.monotonic()
            GLib.timeout_add(80, lambda: self.guarded(self.setup))

        def title(self, actor):
            return f'{self.prefix}-{self.generation}-{actor}'

        def selector(self, actor):
            return json.dumps('address:'+self.addresses[actor])

        def setup(self):
            if self.closing:
                return False
            if time.monotonic()-self.created_at > 20:
                raise RuntimeError('Timed out building the lesson board.')
            if self.pending:
                actor, ratio = self.pending
                found = next((c for c in hypr.request('clients', True) if c['initialTitle'] == self.title(actor)), None)
                if not found:
                    return True
                if found['workspace']['id'] != self.workspace or found['floating']:
                    raise RuntimeError('A lesson window did not tile on the game workspace.')
                self.addresses[actor] = found['address']
                hypr.focus(found['address'])
                if ratio:
                    hypr.run(f'hl.dsp.layout("splitratio {ratio} exact")')
                self.pending = None
            step = next(self.steps, None)
            if step is None:
                hypr.focus(self.addresses[4])
                self.sync()
                self.ready = True
                print(f'READY workspace={self.workspace} lesson={self.game.mission} ship={self.addresses[4]}', flush=True)
                self.smoke_time = time.monotonic()
                return False
            actor, parent, direction, ratio = step
            if parent is not None:
                hypr.focus(self.addresses[parent])
                hypr.run(f'hl.dsp.layout("preselect {direction}")')
            win = Gtk.Window(title=self.title(actor))
            win.set_decorated(False)
            win.set_default_size(480, 300)
            win.connect('delete-event', lambda *_: self.guarded(lambda: self.delete(actor)))
            win.connect('key-press-event', self.key)
            area = Gtk.DrawingArea()
            area.connect('draw', lambda widget, cr, i=actor: draw_tile(cr, widget.get_allocated_width(),
                         widget.get_allocated_height(), self.game, i, self.ready, self.away, time.monotonic()))
            win.add(area)
            self.windows[actor] = win
            win.show_all()
            self.pending = (actor, ratio)
            return True

        def delete(self, actor):
            if self.closing:
                return True
            if not self.ready or self.game.close_exits(actor):
                self.close()
                return True
            if self.game.close_target(actor):
                # This is a real Wayland close request. Destroy only the target;
                # Hyprland naturally reallocates its space to the surviving windows.
                self.windows.pop(actor).destroy()
                self.addresses.pop(actor, None)
                self.geometry.pop(actor, None)
                self.game.geometry.pop(actor, None)
                print(f'TARGET CLOSED actor={actor} remaining={len(self.game.enemies)}', flush=True)
                return True
            # Closing a friendly during active target practice retries that lesson.
            self.windows.pop(actor).destroy()
            self.addresses.pop(actor, None)
            self.ready = False
            mission = self.game.mission
            hit_friendly = actor in self.game.friendlies
            def retry():
                if not self.closing:
                    self.game.load(mission)
                    self.game.say('FRIENDLY HIT / GREEN SHIPS MUST SURVIVE / TRY AGAIN' if hit_friendly else
                                  'CYAN IS YOUR SHIP / CLOSE ONLY RED TARGETS' if mission == 'shoot' else 'WINDOW CLOSED / LET US TRY AGAIN')
                    self.build()
                return False
            GLib.idle_add(lambda: self.guarded(retry))
            return True

        def sync(self):
            clients = hypr.request('clients', True)
            by_address = {c['address']: c for c in clients}
            missing = [i for i,a in self.addresses.items() if a not in by_address]
            if missing:
                raise RuntimeError('A lesson window disappeared unexpectedly. Restart this lesson.')
            self.geometry = {i:by_address[a] for i,a in self.addresses.items()}
            if any(c['workspace']['id'] != self.workspace for c in self.geometry.values()):
                self.away = True
                return
            if self.arena is None:
                x = min(c['at'][0] for c in self.geometry.values())
                y = min(c['at'][1] for c in self.geometry.values())
                right = max(c['at'][0]+c['size'][0] for c in self.geometry.values())
                bottom = max(c['at'][1]+c['size'][1] for c in self.geometry.values())
                self.arena = x,y,right-x,bottom-y
            if self.game.mission == 'float' and self.game.state == 'active':
                craft = self.geometry[4]
                if craft['floating'] and not craft.get('fullscreen') and not self.dock_prepared:
                    self.dock_prepared = True
                    self.game.arena = self.arena
                    w,h = self.game.docking_ship_size
                    x,y,aw,ah = self.arena
                    hypr.run(f'hl.dsp.window.resize({{window={self.selector(4)}, x={int(w)}, y={int(h)}}})',
                             f'hl.dsp.window.move({{window={self.selector(4)}, x={int(x+aw*.25-w/2)}, y={int(y+ah*.5-h/2)}}})')
                    by_address = {c['address']:c for c in hypr.request('clients',True)}
                    self.geometry = {i:by_address[a] for i,a in self.addresses.items()}
                elif not craft['floating']:
                    self.dock_prepared = False
            focused = next((i for i,c in self.geometry.items() if c.get('focusHistoryID') == 0), None)
            self.away = hypr.request('activeworkspace', True)['id'] != self.workspace or focused is None
            # Do not award progress while the user is away from the lesson.
            if not self.away:
                self.game.observe(self.geometry, self.arena, focused)

        def key(self, _window, event):
            def handle():
                if event.state & (Gdk.ModifierType.SUPER_MASK | Gdk.ModifierType.MOD4_MASK | Gdk.ModifierType.MOD1_MASK | Gdk.ModifierType.CONTROL_MASK):
                    return False
                key = Gdk.keyval_name(event.keyval).lower()
                if key in ('escape','q'):
                    self.close()
                elif self.ready:
                    if key in ('space','return'):
                        if self.game.state == 'briefing':
                            self.sync()
                            self.game.start()
                        elif self.game.state == 'complete':
                            if self.game.index+1 < len(MISSIONS):
                                self.game.load(MISSIONS[self.game.index+1][0])
                                self.build()
                        else:
                            self.game.paused = not self.game.paused
                    elif key == 'r':
                        self.game.load(self.game.mission)
                        self.build()
                    elif key in '123456' and len(key) == 1:
                        self.game.load(MISSIONS[int(key)-1][0])
                        self.build()
                return True
            return self.guarded(handle)

        def frame(self):
            if self.closing:
                return False
            now = time.monotonic()
            dt = min(now-self.last_tick, .1)
            self.last_tick = now
            if self.ready:
                if now-self.last_sync > .08:
                    self.sync()
                    self.last_sync = now
                if not self.away and not args.smoke_test:
                    self.game.advance(dt)
                if args.smoke_test and now-self.smoke_time > .8:
                    self.smoke_time = now
                    self.smoke()
            for win in list(self.windows.values()):
                win.queue_draw()
            return not self.closing

        def action(self, expression):
            hypr.focus(self.addresses[4])
            hypr.run(expression)
            self.sync()

        def smoke(self):
            stage = self.smoke_stage
            if stage == 0:
                assert len(self.geometry) == SECTORS
                assert len({sector(c, self.arena) for c in self.geometry.values()}) == SECTORS
                widths = [c["size"][0] for c in self.geometry.values()]
                heights = [c["size"][1] for c in self.geometry.values()]
                assert max(widths)/min(widths) < 1.15 and max(heights)/min(heights) < 1.15
                self.game.start()
                before = self.game.ship_slot
                self.action('hl.dsp.window.swap({direction="l"})')
                assert self.game.ship_slot != before
                print('PASS native asteroid movement', flush=True)
                self.game.load('lasers'); self.build()
            elif stage == 1:
                assert len(self.geometry) == 2
                self.game.start()
                self.action('hl.dsp.layout("togglesplit")')
                from game import side
                assert side(self.geometry[4],self.arena) in ('top','bottom')
                before = side(self.geometry[4],self.arena)
                self.action(f'hl.dsp.window.swap({{target={self.selector(0)}}})')
                assert side(self.geometry[4],self.arena) != before
                print('PASS native two-window rotation and swap', flush=True)
                self.game.load('shoot'); self.build()
            elif stage == 2:
                self.game.start()
                hypr.focus(self.addresses[0])
                self.sync()
                assert self.game.focused == 0
                assert 'DESTROY' in self.game.instruction()
                hypr.run(f'hl.dsp.window.close({{window={self.selector(0)}}})')
            elif stage == 3:
                assert len(self.windows) == 15 and 0 not in self.game.enemies
                hypr.focus(self.addresses[1]); self.sync()
                assert 'DO NOT FIRE' in self.game.instruction()
                hypr.run(*(f'hl.dsp.window.close({{window={self.selector(actor)}}})' for actor in sorted(self.game.enemies)))
            elif stage == 4:
                assert self.game.state == 'complete'
                assert set(self.windows) == FRIENDLIES | {4}
                print('PASS ten real enemy closes; five friendlies preserved', flush=True)
            elif stage == 5:
                self.game.load('float'); self.build()
            elif stage == 6:
                self.game.start()
                self.action(f'hl.dsp.window.float({{window={self.selector(4)}, action="on"}})')
                assert self.game.step == 1
                dx,dy,dw,dh = self.game.dock_rect
                bx,by = dx+dw/2,dy+dh/2
                w,h = self.geometry[4]['size']
                self.action(f'hl.dsp.window.move({{window={self.selector(4)}, x={int(bx-w/2)}, y={int(by-h/2)}}})')
                assert self.game.step == 2
                self.action(f'hl.dsp.window.float({{window={self.selector(4)}, action="off"}})')
                assert self.game.state == 'complete'
                print('PASS compact undock, whole-window docking bay, and landing', flush=True)
                self.game.load('resize'); self.build()
            elif stage == 7:
                self.game.start()
                amount = int(self.game.baseline_width*.3)
                self.action(f'hl.dsp.window.resize({{window={self.selector(4)}, x={amount}, y=0, relative=true}})')
                self.game.advance(.7)
                assert self.game.step == 1
                self.action(f'hl.dsp.window.resize({{window={self.selector(4)}, x={-amount}, y=0, relative=true}})')
                self.game.advance(.7)
                assert self.game.state == 'complete'
                print('PASS native cargo width and restoration', flush=True)
                self.game.load('invasion'); self.build()
            elif stage == 8:
                self.game.start()
                self.action(f'hl.dsp.window.fullscreen({{window={self.selector(4)}, mode="fullscreen"}})')
                assert self.game.step == 1
                self.game.advance(2.6)
                assert self.game.step == 2 and self.game.charge == 1
                self.action(f'hl.dsp.window.fullscreen({{window={self.selector(4)}, mode="maximized"}})')
                assert self.game.step == 3 and self.geometry[4]['fullscreen'] == 1
                print('PASS fullscreen charge and native maximize release', flush=True)
            elif stage == 9:
                self.game.advance(3.1)
                assert self.game.state == 'complete'
                print('PASS weapon animation completes invasion mission', flush=True)
                self.game.load('shoot'); self.build()
            elif stage == 10:
                self.game.start()
                hypr.run(f'hl.dsp.window.close({{window={self.selector(1)}}})')
            else:
                assert self.game.state == 'briefing' and len(self.windows) == 16
                assert 'FRIENDLY HIT' in self.game.feedback
                print('PASS friendly-fire retry and explanation', flush=True)
                self.close()
            self.smoke_stage += 1

        def close(self):
            if self.closing:
                return
            self.closing = True
            for win in list(self.windows.values()):
                win.destroy()
            try:
                if self.rule_installed:
                    hypr.request(f'eval if {self.rule} then {self.rule}:set_enabled(false); {self.rule}=nil end')
                if hypr.request('activeworkspace', True)['id'] == self.workspace:
                    previous = self.previous if self.previous.isdigit() else 'name:'+self.previous
                    hypr.run(f'hl.dsp.focus({{workspace={json.dumps(previous)}}})')
                    if self.previous_window in {c['address'] for c in hypr.request('clients', True)}:
                        hypr.focus(self.previous_window)
            except Exception as error:
                print(f'Cleanup: {error}', file=sys.stderr)
            if Gtk.main_level():
                Gtk.main_quit()

    GLib.set_prgname('hyprsplitter')
    GLib.set_application_name('Hyprsplitter')
    app = App()
    for sig in (signal.SIGINT, signal.SIGTERM):
        GLibUnix.signal_add(GLib.PRIORITY_DEFAULT, sig, lambda: app.close() or False)
    try:
        app.begin()
        Gtk.main()
    finally:
        app.close()
    return 1 if app.error else 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (RuntimeError, OSError, ImportError) as error:
        print(f'Hyprsplitter: {error}', file=sys.stderr)
        sys.exit(1)

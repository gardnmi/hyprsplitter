#!/usr/bin/env python3
"""Keep the walker alive by swapping real Hyprland windows."""
import argparse
import json
import math
import os
from pathlib import Path
import signal
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from hyprsplitter import Hyprland
from model import Level, rain_cells
from experiments.theme import rgb, FONT
from experiments.visuals import walker as paint_walker, cloud as paint_cloud
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
gi.require_version('GLibUnix', '2.0')
from gi.repository import Gtk, Gdk, GLib, GLibUnix
import cairo


def text(cr, value, x, y, size=15, color=None):
    cr.set_source_rgb(*(color or rgb('foreground')))
    cr.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    cr.set_font_size(size)
    cr.move_to(x, y)
    cr.show_text(value)


class Game:
    def __init__(self, state_file=None, level=1):
        self.hypr = Hyprland()
        self.level = Level(level)
        self.prefix = f'WalkingMan-{os.getpid()}'
        self.rule = f'walking_man_{os.getpid()}'
        self.windows, self.areas, self.clients = {}, {}, {}
        self.ready = self.closed = False
        self.error = None
        self.state_file = state_file
        self.started = self.last = time.monotonic()
        self.away = False
        self.rain_time = 0.
        self.cloud_motion = 0.
        self.previous_cloud = None
        self.gait = 0.
        self.previous = self.hypr.request('activeworkspace', True)['name']
        self.previous_window = self.hypr.request('activewindow', True).get('address')
        occupied = {w['id'] for w in self.hypr.request('workspaces', True)}
        self.workspace = next(i for i in range(2, 10000) if i not in occupied)
        if self.hypr.request('getoption general:layout', True).get('str') != 'dwindle':
            raise RuntimeError('This level requires the Hyprland dwindle layout.')
        for option in ('preserve_split', 'use_active_for_splits'):
            if not self.hypr.request('getoption dwindle:' + option, True).get('bool'):
                raise RuntimeError(f'This level requires dwindle:{option} enabled.')
        self.hypr.request(f'eval {self.rule}=hl.window_rule({{name="{self.rule}",match={{initial_title="^{self.prefix}-(path|fire|goal)$"}},workspace="{self.workspace}",tile=true,no_anim=false,opacity="1 override 1 override"}})')
        try:
            self.hypr.request(f'eval {self.rule}_cloud=hl.window_rule({{name="{self.rule}_cloud",match={{initial_title="^{self.prefix}-cloud$"}},workspace="{self.workspace}",float=true,no_anim=false,opacity="1 override 1 override"}})')
            self.hypr.run(f'hl.dsp.focus({{workspace="{self.workspace}"}})')
            self.build()
            GLib.timeout_add(100, self.sync)
            GLib.timeout_add(33, self.tick)
            GLibUnix.signal_add(GLib.PRIORITY_DEFAULT, signal.SIGTERM, self.close)
            GLibUnix.signal_add(GLib.PRIORITY_DEFAULT, signal.SIGINT, self.close)
        except BaseException:
            self.close()
            raise

    def build(self):
        self.ready = False
        for win in self.windows.values():
            win.destroy()
        self.windows, self.areas, self.clients = {}, {}, {}
        self.pending = None
        steps = [('path', None, None, 'r'), ('goal', 'path', 1.333333, 'r'), ('fire', 'path', 1, 'r')]
        if self.level.number == 2:
            steps.append(('cloud', None, None, 'r'))
        self.steps = iter(steps)
        self.invalid_layout = True
        self.started = time.monotonic()

    def create_next(self):
        step = next(self.steps, None)
        if step is None:
            self.ready = True
            self.hypr.focus(self.clients['cloud' if self.level.number == 2 else 'path']['address'])
            shortcut = 'Drag cloud over fire' if self.level.number == 2 else 'Super+Shift+Right on walker'
            print(f'READY workspace={self.workspace}: Space starts; {shortcut}; R resets; Esc closes.', flush=True)
            return
        role, parent, ratio, direction = step
        if parent:
            self.hypr.focus(self.clients[parent]['address'])
            self.hypr.run(f'hl.dsp.layout("preselect {direction}")')
        win = Gtk.Window(title=f'{self.prefix}-{role}')
        win.set_decorated(False)
        win.set_default_size(320, 220) if role == 'cloud' else win.set_default_size(480, 370)
        win.connect('delete-event', lambda *_: self.close())
        win.connect('key-press-event', self.key)
        area = Gtk.DrawingArea()
        area.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        area.connect('button-press-event', self.press, role)
        area.connect('draw', self.draw, role)
        win.add(area)
        self.windows[role], self.areas[role] = win, area
        win.show_all()
        self.pending = (role, ratio)

    def press(self, area, event, role):
        if event.button == 1 and role == 'cloud':
            self.windows['cloud'].begin_move_drag(1, int(event.x_root), int(event.y_root), event.time)
        elif event.button == 1 and event.y > area.get_allocated_height() - 58 and self.ready:
            if self.level.status == 'ready':
                self.level.status = 'walking'
            elif self.level.status == 'won' and self.level.number == 1:
                self.next_level()
            elif self.level.status in ('won', 'lost'):
                self.reset()
        return True

    def next_level(self):
        self.level = Level(2)
        self.build()

    def reset(self):
        self.level.reset()
        self.build()

    def key(self, win, event):
        key = Gdk.keyval_name(event.keyval).lower()
        if key == 'escape':
            self.close()
        elif key == 'r':
            self.reset()
        elif key == 'space' and self.ready:
            if self.level.status == 'ready':
                self.level.status = 'walking'
            elif self.level.status == 'won' and self.level.number == 1:
                self.next_level()
            elif self.level.status in ('won', 'lost'):
                self.reset()
        return key in ('escape', 'r', 'space')

    def sync(self):
        if self.closed:
            return False
        try:
            clients = self.hypr.request('clients', True)
            self.clients = {role: next((c for c in clients if c.get('initialTitle') == f'{self.prefix}-{role}'), None) for role in self.windows}
            if not self.ready:
                if time.monotonic() - self.started > 15:
                    raise RuntimeError('Timed out building tiled level')
                if self.pending:
                    role, ratio = self.pending
                    client = self.clients.get(role)
                    if not client:
                        return True
                    if client['floating'] != (role == 'cloud') or client['workspace']['id'] != self.workspace:
                        raise RuntimeError('A game window did not tile on its workspace')
                    self.hypr.focus(client['address'])
                    if role == 'cloud':
                        path = self.clients['path']
                        x, y = path['at']
                        selector = json.dumps('address:' + client['address'])
                        self.hypr.run(f'hl.dsp.window.resize({{window={selector},x=320,y=220}})',
                                      f'hl.dsp.window.move({{window={selector},x={x + 80},y={y + 150}}})')
                    if ratio:
                        self.hypr.run(f'hl.dsp.layout("splitratio {ratio} exact")')
                    self.pending = None
                self.create_next()
                return True
            if not all(self.clients.values()):
                self.close()
                return False
            self.away = self.hypr.request('activeworkspace', True)['id'] != self.workspace
            for role, client in self.clients.items():
                selector = json.dumps('address:' + client['address'])
                if client['workspace']['id'] != self.workspace:
                    self.hypr.run(f'hl.dsp.window.move({{window={selector},workspace="{self.workspace}",follow=false}})')
                    return True
                if client['floating'] != (role == 'cloud'):
                    action = 'on' if role == 'cloud' else 'off'
                    self.hypr.run(f'hl.dsp.window.float({{window={selector},action="{action}"}})')
                    return True
            self.invalid_layout = True
            self.level.wet = False
            self.level.wet_cells = [False] * 12
            order = sorted(('path', 'fire', 'goal'), key=lambda r: tuple(self.clients[r]['at']))
            if order[-1] != 'goal':
                goal = json.dumps('address:' + self.clients['goal']['address'])
                other = json.dumps('address:' + self.clients[order[-1]]['address'])
                self.hypr.run(f'hl.dsp.window.swap({{window={goal},target={other}}})')
                return True
            if self.level.number == 2:
                # The three route tiles are locked in level two; cloud floats.
                if order[0] != 'path':
                    walker = json.dumps('address:' + self.clients['path']['address'])
                    other = json.dumps('address:' + self.clients[order[0]]['address'])
                    self.hypr.run(f'hl.dsp.window.swap({{window={walker},target={other}}})')
                    return True
                self.level.order = ['path', 'fire', 'goal']
                c, f = self.clients['cloud'], self.clients['fire']
                if self.previous_cloud:
                    self.cloud_motion += (c['at'][0] - self.previous_cloud[0]) * .7
                self.previous_cloud = tuple(c['at'])
                tops = [self.clients[r]['at'][1] for r in ('path', 'fire', 'goal')]
                self.invalid_layout = max(tops) - min(tops) > 30
                self.level.wet_cells = rain_cells(c, f) if not self.invalid_layout else [False] * 12
                self.level.wet = any(self.level.wet_cells)
            else:
                # The compositor owns the positions; read its tiled order.
                self.level.order = order
                tops = [c['at'][1] for c in self.clients.values()]
                self.invalid_layout = max(tops) - min(tops) > 30
            if self.state_file:
                self.state_file.write_text(json.dumps({'level': self.level.number, 'heat': self.level.heat, 'flames': self.level.flames, 'extinguished': self.level.extinguished, 'wet': self.level.wet, 'status': self.level.status, 'room': self.level.room, 'x': self.level.x, 'order': self.level.order, 'prefix': self.prefix, 'workspace': self.workspace, 'away': self.away, 'windows': {r: {k: c[k] for k in ('address', 'at', 'size', 'floating', 'workspace')} for r, c in self.clients.items()}}))
        except Exception as exc:
            self.error = str(exc)
            print(f'ERROR: {exc}', file=sys.stderr, flush=True)
            self.close()
            return False
        return True

    def tick(self):
        if self.closed:
            return False
        now = time.monotonic()
        dt, self.last = min(.1, now - self.last), now
        self.rain_time = now - self.started
        self.cloud_motion *= .85
        if self.level.status == 'walking' and not self.away:
            self.gait += dt * 9
        if self.ready and not self.away and not getattr(self, 'invalid_layout', False):
            previous_room = self.level.room
            self.level.step(dt, self.clients)
            if self.level.room != previous_room:
                # Hand both drawing ownership and keyboard focus to the tile
                # he has just entered; never keep controlling the empty start.
                self.hypr.focus(self.clients[self.level.room]['address'])
        for area in self.areas.values():
            area.queue_draw()
        return True

    def draw(self, area, cr, role):
        w, h = area.get_allocated_width(), area.get_allocated_height()
        t = time.monotonic() - self.started
        floor = h - 95
        palette = {'path': (.10, .17, .23), 'fire': (.23, .105, .09), 'goal': (.075, .20, .17), 'cloud': (.09, .19, .28)}
        cr.set_source_rgb(*rgb('background'))
        cr.paint()
        if role == 'cloud':
            self.draw_cloud(cr, w, h, t)
            return False
        text(cr, f'KEEP HIM ALIVE  /  LEVEL {self.level.number:02}', 22, 30, 12)
        title = 'The walker' if role == self.level.room else {'path': 'Clear path', 'fire': 'Fire ahead', 'goal': 'Safe home', 'cloud': 'Rain cloud'}[role]
        text(cr, title, 22, 65, 27, (.96, .96, .90))
        subtitle = {'path': 'Swap this room past the fire.', 'fire': 'Do not let him walk into this room.', 'goal': 'FIXED WINDOW  /  Get him to the door.', 'cloud': ''}[role]
        if self.level.number == 2:
            subtitle = {'path': 'LOCKED ROUTE / Put out the fire ahead.',
                        'fire': 'Rain from above makes this room safe.',
                        'goal': 'FIXED WINDOW / Get him to the door.',
                        'cloud': 'DRAG ME / Hold the rain over the flames.'}[role]
        text(cr, subtitle, 22, 89, 13)
        cr.set_source_rgb(.28, .39, .39)
        cr.rectangle(0, floor, w, 4)
        cr.fill()
        for i in range(10):
            cr.set_source_rgba(.7, .8, .8, .10)
            cr.rectangle(i * w / 9, floor + 12, 18, 2)
            cr.fill()
        if role == 'fire':
            for i, fuel in enumerate(self.level.flames):
                x = w * (.32 + .36 * i / 11)
                height = (65 + 27 * math.sin(t * 7 + i * 2)) * fuel
                if fuel <= .001:
                    continue
                for scale, color in ((1, (1, .25, .04)), (.60, (1, .69, .13))):
                    cr.set_source_rgb(*color)
                    cr.move_to(x - 16 * scale, floor)
                    cr.curve_to(x - 30 * scale, floor - height * .5, x + 12, floor - height * scale, x, floor - height * scale)
                    cr.curve_to(x + 1, floor - height * .3, x + 29 * scale, floor - 17, x + 16 * scale, floor)
                    cr.fill()
            if self.level.number == 2:
                label = 'FIRE OUT / Safe to cross' if self.level.heat <= .001 else f'FIRE {self.level.heat:.0%}'
                text(cr, label, 22, 120, 16, (.5, .9, .8))
                if self.level.wet:
                    self.draw_rain(cr, 'fire', w, h)
        elif role == 'goal':
            cr.set_source_rgb(.22, .70, .48)
            cr.rectangle(w * .65 - 27, floor - 107, 66, 107)
            cr.fill()
            cr.set_source_rgb(.04, .17, .14)
            cr.rectangle(w * .65 - 20, floor - 98, 52, 98)
            cr.fill()
            text(cr, 'EXIT', w * .65 - 17, floor - 118, 17, (.5, 1, .69))
            cr.set_source_rgb(.9, .85, .4)
            cr.arc(w * .65 + 21, floor - 49, 3, 0, math.tau)
            cr.fill()
        else:
            text(cr, 'WALK THIS WAY  >', 22, floor - 112, 12, (.4, .65, .76))
        if role == self.level.room:
            x = self.level.x * w
            cr.save();cr.translate(x,floor);cr.scale(1.,1.)
            paint_walker(cr,0,0,t,walking=self.level.status=='walking',
                         happy=self.level.status=='won',phase=self.gait)
            cr.restore()
        status = self.level.status
        if status == 'ready':
            message = 'SPACE / CLICK HERE TO START'
        elif status == 'walking':
            message = ('Drag the floating cloud over the fire' if self.level.number == 2 else 'SUPER + SHIFT + RIGHT  /  Swap walker past fire')
        elif status == 'won':
            message = 'HE MADE IT! / SPACE for level 2' if self.level.number == 1 else 'HE MADE IT! / Both levels complete. R to replay'
        else:
            message = 'TOO HOT!  /  R to try again'
        if getattr(self, 'invalid_layout', False):
            message = 'PAUSED: restore the route with R.'
        text(cr, message, 22, h - 43, 13, (.6, 1, .76) if status == 'won' else (.96, .84, .64))
        text(cr, 'R  restart     ESC  close', 22, h - 20, 11)
        return False

    def draw_cloud(self, cr, w, h, t):
        self.draw_rain(cr, 'cloud', w, h)
        paint_cloud(cr,w,h,t,wet=self.level.wet,motion=self.cloud_motion)

    def draw_rain(self, cr, role, w, h):
        cloud = self.clients.get('cloud')
        target = self.clients.get(role)
        if not cloud or not target:
            return
        cx, cy = cloud['at']
        cw, ch = cloud['size']
        tx, ty = target['at']
        source_y = cy + ch * 111 / 220
        top = source_y if role == 'cloud' else max(cy + ch, ty)
        bottom = ty + h if role == 'cloud' else ty + h - 95
        left, width = cx + cw * .25, cw * .5
        cr.save()
        cr.rectangle(left - tx, top - ty, width, max(0, bottom - top))
        cr.clip()
        cr.set_source_rgba(.35, .76, 1, .6)
        cr.set_line_width(2)
        # Both windows draw the same world-space stream, using the same frame
        # clock, 190 logical pixels/second and 96-pixel spacing. No per-window
        # wrap length or cloud scaling can change a drop's speed or phase.
        for i in range(16):
            x = left + width * ((i * .6180339) % 1)
            first = source_y + (self.rain_time * 190 + i * 41) % 96
            n = max(0, math.floor((top - first - 11) / 96))
            y = first + n * 96
            while y < bottom:
                cr.move_to(x - tx, y - ty)
                cr.line_to(x - tx - 3, y - ty + 11)
                y += 96
        cr.stroke()
        cr.restore()

    def close(self):
        if self.closed:
            return False
        self.closed = True
        try:
            return_to_previous = self.hypr.request('activeworkspace', True)['id'] == self.workspace
        except Exception:
            return_to_previous = False
        for win in self.windows.values():
            win.destroy()
        try:
            self.hypr.request(f'eval if {self.rule}_cloud then {self.rule}_cloud:set_enabled(false); {self.rule}_cloud=nil end')
            self.hypr.request(f'eval if {self.rule} then {self.rule}:set_enabled(false); {self.rule}=nil end')
        except Exception:
            pass
        if return_to_previous:
            try:
                self.hypr.run(f'hl.dsp.focus({{workspace={json.dumps(self.previous)}}})')
                if self.previous_window:
                    self.hypr.focus(self.previous_window)
            except Exception:
                pass
        if Gtk.main_level():
            Gtk.main_quit()
        return False


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--state-file', type=Path)
    parser.add_argument('--level', type=int, choices=(1, 2), default=1)
    args = parser.parse_args()
    GLib.set_prgname('walking-man-poc')
    game = Game(args.state_file, args.level)
    try:
        Gtk.main()
    finally:
        game.close()
    if game.error:
        raise SystemExit(game.error)


if __name__ == '__main__':
    main()

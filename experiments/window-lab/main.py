#!/usr/bin/env python3
"""Ten real-window interaction sketches for Keep Him Alive."""
import argparse
import json
import os
from pathlib import Path
import signal
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from hyprsplitter import Hyprland
from model import DEMOS, State, linked
from art import icon, label, box, GREEN, BLUE, WHITE
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
gi.require_version('GLibUnix', '2.0')
from gi.repository import Gtk, Gdk, GLib, GLibUnix
import cairo


class Lab:
    def __init__(self, index, state_file=None):
        self.hypr = Hyprland()
        self.state = State(index)
        self.state_file = state_file
        self.prefix = f'WindowLab-{os.getpid()}'
        self.rule = f'window_lab_{os.getpid()}'
        self.windows, self.areas, self.geometry = {}, {}, {}
        self.closed = self.ready = False
        self.error = None
        self.previous = self.hypr.request('activeworkspace', True)['name']
        self.previous_window = self.hypr.request('activewindow', True).get('address')
        occupied = {w['id'] for w in self.hypr.request('workspaces', True)}
        self.workspace = next(i for i in range(2, 10000) if i not in occupied)
        monitor = next(m for m in self.hypr.request('monitors', True) if m['focused'])
        mw, mh = monitor['width']/monitor['scale'], monitor['height']/monitor['scale']
        self.origin = (int(monitor['x']+mw/2-170), int(monitor['y']+mh/2-90))
        self.started = self.last = time.monotonic()
        self.time = 0
        self.hypr.request(f'eval {self.rule}=hl.window_rule({{name="{self.rule}",match={{initial_title="^{self.prefix}-.*$"}},workspace="{self.workspace}",float=true,no_anim=true,rounding=16,opacity="1 override 1 override"}})')
        try:
            self.hypr.run(f'hl.dsp.focus({{workspace="{self.workspace}"}})')
            for role in ('target', 'tool'):
                win = Gtk.Window(title=f'{self.prefix}-{role}')
                win.set_decorated(False)
                win.set_default_size(*( (440,340) if role=='target' else (300,240)))
                win.connect('delete-event', lambda *_: self.close())
                win.connect('key-press-event', self.key)
                area = Gtk.DrawingArea()
                area.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
                area.connect('button-press-event', self.press, role)
                area.connect('draw', self.draw, role)
                win.add(area)
                self.windows[role], self.areas[role] = win, area
                win.show_all()
            GLib.timeout_add(80, self.sync)
            GLib.timeout_add(33, self.tick)
            GLibUnix.signal_add(GLib.PRIORITY_DEFAULT, signal.SIGTERM, self.close)
            GLibUnix.signal_add(GLib.PRIORITY_DEFAULT, signal.SIGINT, self.close)
        except BaseException:
            self.close()
            raise

    def position(self):
        x,y = self.origin
        positions = {'target':(x,y,440,340), 'tool':(x-380,max(50,y-190),300,240)}
        for role,(a,b,w,h) in positions.items():
            sel=json.dumps('address:'+self.geometry[role]['address'])
            self.hypr.run(f'hl.dsp.window.resize({{window={sel},x={w},y={h}}})',
                          f'hl.dsp.window.move({{window={sel},x={a},y={b}}})')

    def select(self, index):
        self.state = State(index % len(DEMOS))
        if self.ready:
            self.position()

    def key(self, win, event):
        key = Gdk.keyval_name(event.keyval).lower()
        if key == 'escape': self.close()
        elif key in ('n','right'): self.select(self.state.index+1)
        elif key in ('p','left'): self.select(self.state.index-1)
        elif key == 'r': self.select(self.state.index)
        elif key in ('1','2','3','4','5','6','7','8','9','0'):
            self.select((int(key)-1)%10)
        return True

    def press(self, area, event, role):
        if event.button != 1: return False
        if role == 'target' and event.y > area.get_allocated_height()-43:
            if event.x < area.get_allocated_width()/3: self.select(self.state.index-1)
            elif event.x > area.get_allocated_width()*2/3: self.select(self.state.index+1)
            else: self.select(self.state.index)
        else:
            self.windows[role].begin_move_drag(1,int(event.x_root),int(event.y_root),event.time)
        return True

    def sync(self):
        if self.closed: return False
        try:
            clients=self.hypr.request('clients',True)
            self.geometry={r:next((c for c in clients if c.get('initialTitle')==f'{self.prefix}-{r}'),None) for r in self.windows}
            if not all(self.geometry.values()):
                if self.ready: self.close(); return False
                if time.monotonic()-self.started>10: raise RuntimeError('Windows did not appear')
                return True
            if not self.ready:
                self.position()
                self.ready=True
                print(f'READY: workspace {self.workspace}; N/P demos, R reset, Esc close.',flush=True)
            visible=self.hypr.request('activeworkspace',True)['id']==self.workspace
            self.visible=visible
            self.linked=visible and linked(self.state.demo,self.geometry['tool'],self.geometry['target'])
            if self.state_file:
                payload={'pid':os.getpid(),'workspace':self.workspace,'demo':self.state.index+1,
                         'name':self.state.demo.name,'active':self.state.active,'progress':self.state.progress,'won':self.state.won,
                         'windows':{r:{k:c[k] for k in ('address','at','size','workspace','floating')} for r,c in self.geometry.items()}}
                tmp=self.state_file.with_suffix('.tmp');tmp.write_text(json.dumps(payload));tmp.replace(self.state_file)
        except Exception as exc:
            self.error=str(exc);print(f'ERROR: {exc}',file=sys.stderr,flush=True);self.close();return False
        return True

    def tick(self):
        if self.closed:return False
        now=time.monotonic();dt=min(.1,now-self.last);self.last=now
        self.time=now-self.started
        if self.ready and getattr(self,'visible',False):
            self.state.step(dt,getattr(self,'linked',False))
        for area in self.areas.values():area.queue_draw()
        return True

    def draw(self, area, cr, role):
        w,h=area.get_allocated_width(),area.get_allocated_height()
        gradient=cairo.LinearGradient(0,0,0,h)
        gradient.add_color_stop_rgb(0,.07,.13,.19);gradient.add_color_stop_rgb(1,.025,.045,.075)
        cr.set_source(gradient);cr.paint()
        demo=self.state.demo
        if role=='tool':
            # Same physical illustration scale in both windows; resizing does
            # not stretch rain, beams, or other effects to different speeds.
            cr.save();cr.translate((w-300)/2,(h-190)/2)
            icon(cr,demo.tool,self.state.progress,self.state.active,self.time)
            cr.restore()
            return False
        label(cr,f'{self.state.index+1:02} / 10    {demo.name}',20,30,20)
        label(cr,demo.hint,20,56,13,(.61,.73,.82))
        cr.save();cr.translate((w-300)/2,70)
        icon(cr,demo.target,self.state.progress,self.state.active,self.time)
        cr.restore()
        y=h-72
        box(cr,20,y,w-40,4,(.16,.24,.3))
        box(cr,20,y,(w-40)*self.state.progress,4,GREEN if self.state.won else BLUE)
        status=demo.result if self.state.won else ('CONNECTED' if self.state.active else 'Move the object window into position')
        label(cr,status,20,h-48,12,GREEN if self.state.won else WHITE)
        label(cr,'<  P previous',20,h-18,12)
        label(cr,'R reset',w/2-22,h-18,12)
        label(cr,'N next  >',w-83,h-18,12)
        return False

    def close(self):
        if self.closed:return False
        self.closed=True
        try: restore=self.hypr.request('activeworkspace',True)['id']==self.workspace
        except Exception:restore=False
        for win in self.windows.values():win.destroy()
        try:self.hypr.request(f'eval if {self.rule} then {self.rule}:set_enabled(false); {self.rule}=nil end')
        except Exception:pass
        if restore:
            try:
                self.hypr.run(f'hl.dsp.focus({{workspace={json.dumps(self.previous)}}})')
                if self.previous_window:self.hypr.focus(self.previous_window)
            except Exception:pass
        if Gtk.main_level():Gtk.main_quit()
        return False


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--demo',type=int,choices=range(1,11),default=1)
    parser.add_argument('--state-file',type=Path)
    args=parser.parse_args()
    GLib.set_prgname('window-interaction-lab')
    lab=Lab(args.demo-1,args.state_file)
    try:Gtk.main()
    finally:lab.close()
    if lab.error:raise SystemExit(lab.error)


if __name__=='__main__':main()

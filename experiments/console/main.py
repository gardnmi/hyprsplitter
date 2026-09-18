#!/usr/bin/env python3
"""Omatari: a console and discoverable floating cartridge windows."""
import json,os,signal,subprocess,sys,time
import cairo
import logging
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
import gi
gi.require_version('Gtk','3.0');gi.require_version('Gdk','3.0');gi.require_version('GLibUnix','2.0')
from gi.repository import Gtk,Gdk,GLib,GLibUnix
from hyprsplitter import Hyprland
from catalog import GAMES,ROOT,CONSOLE,CARTRIDGE,aligned,starting_layout
from art import console,cartridge
from insertion import DURATION,seat_rect,travel,kick

class Launcher:
 def __init__(self,*,focus=True,workspace=None,start_rects=None):
  logdir=Path(os.environ.get('XDG_CACHE_HOME',Path.home()/'.cache'))/'hyprsplitter'
  logdir.mkdir(parents=True,exist_ok=True)
  logging.basicConfig(filename=logdir/'console.log',level=logging.INFO,format='%(asctime)s %(message)s',force=True)
  logging.info('Launcher starting')
  self.missing_since=None
  self.hypr=Hyprland();self.closed=False;self.child=None;self.log=None
  self.previous=self.hypr.request('activeworkspace',True)['name']
  used={w['id'] for w in self.hypr.request('workspaces',True)}
  self.workspace=workspace if workspace is not None else next(i for i in range(2,1000) if i not in used)
  m=next(m for m in self.hypr.request('monitors',True) if m['focused'])
  mw,mh=int(m['width']/m['scale']),int(m['height']/m['scale'])
  self.starts,self.scale=starting_layout((m['x'],m['y'],mw,mh))
  if start_rects:self.starts.update(start_rects)
  self.rects=dict(self.starts);self.placed=False;self.reset_pending=False
  self.prefix=f'HyprConsole-{os.getpid()}';self.rule=f'hyprconsole_{os.getpid()}'
  self.hypr.request(f'eval {self.rule}=hl.window_rule({{name="{self.rule}",match={{initial_title="^{self.prefix}-.*$"}},workspace="{self.workspace}",float=true,no_anim=true,rounding=0,border_size=0}})')
  if focus:self.hypr.run(f'hl.dsp.focus({{workspace="{self.workspace}"}})')
  self.windows={};self.clients={};self.candidate=None;self.since=0.;self.inserting=None;self.status='INSERT A CARTRIDGE';self.last_rect=None;self.armed=None
  for role,rect in self.starts.items():
   win=Gtk.Window(title=f'{self.prefix}-{role}');win.set_focus_on_map(focus);win.set_decorated(False);win.set_resizable(False);win.set_default_size(*rect[2:])
   win.set_app_paintable(True)
   visual=win.get_screen().get_rgba_visual()
   if visual:win.set_visual(visual)
   win.connect('delete-event',lambda *_:self.close('window close requested') or True);win.connect('key-press-event',self.key)
   area=Gtk.DrawingArea();area.add_events(Gdk.EventMask.BUTTON_PRESS_MASK);area.connect('button-press-event',self.drag,win);area.connect('draw',self.draw,role)
   win.add(area);win.show_all();self.windows[role]=win
  self.begin=time.monotonic();self.visible=True
  GLib.timeout_add(80,self.sync);GLib.timeout_add(33,self.animate)
  for sig in (signal.SIGTERM,signal.SIGINT):GLibUnix.signal_add(GLib.PRIORITY_DEFAULT,sig,self.close)
 def drag(self,area,event,win):
  if event.button==1 and not self.inserting:
   if self.armed and win is self.windows[self.armed]:
    game=next(g for g in GAMES if g['id']==self.armed)
    logging.info('Cartridge clicked: %s',game['id'])
    self.inserting=(game,time.monotonic());self.armed=None
    return True
   if win is self.windows.get('console'):
    allocation=area.get_allocation();x=event.x*560/allocation.width;y=event.y*360/allocation.height
    if 210<=y<=239 and 47<=x<=95:
     self.status='ESC TO POWER OFF';return True
    if 210<=y<=239 and 108<=x<=156:self.reset_pending=True;return True
   win.begin_move_drag(1,int(event.x_root),int(event.y_root),event.time)
  return True
 def key(self,win,event):
  key=Gdk.keyval_name(event.keyval).lower()
  if key=='escape':self.close('Escape pressed')
  elif key=='r' and not self.child:self.reset_pending=True;self.inserting=None;self.candidate=None;self.status='INSERT A CARTRIDGE';self.armed=None
  return True
 def position(self,role,rect):
  sel=json.dumps('address:'+self.clients[role]['address']);x,y,w,h=rect
  self.hypr.run(f'hl.dsp.window.resize({{window={sel},x={w},y={h}}})',f'hl.dsp.window.move({{window={sel},x={x},y={y}}})')
 def sync(self):
  if self.closed:return False
  try:
   active=self.hypr.request('activeworkspace',True)['id'];self.visible=active==self.workspace
   if self.child:
    code=self.child.poll()
    if code is None:return True
    self.child=None
    if self.log:self.log.close();self.log=None
    self.status='WELCOME BACK' if code==0 else 'START FAILED / SEE LOG'
    self.inserting=None;self.candidate=None;self.reset_pending=True
   clients=self.hypr.request('clients',True)
   self.clients={role:next((c for c in clients if c.get('initialTitle')==f'{self.prefix}-{role}'),None) for role in self.windows}
   if not all(self.clients.values()):
    now=time.monotonic()
    if getattr(self,'missing_since',None) is None:self.missing_since=now
    if now-self.missing_since>3:
     self.close('Windows missing: '+','.join(r for r,c in self.clients.items() if not c));return False
    return True
   self.missing_since=None
   if not self.placed or self.reset_pending:
    for role,rect in self.starts.items():
     self.position(role,rect);self.windows[role].set_opacity(1)
    self.armed=None;self.inserting=None;self.candidate=None
    self.rects=dict(self.starts);self.placed=True;self.reset_pending=False;self.last_rect=None
    return True
   self.rects={role:tuple(c['at']+c['size']) for role,c in self.clients.items()}
   if not self.visible:return True
   now=time.monotonic()
   if self.inserting:
    if now-self.inserting[1]>DURATION:self.launch(self.inserting[0])
    return True
   candidate=next((g for g in GAMES if self.clients[g['id']]['workspace']['id']==self.workspace and aligned(self.rects['console'],self.rects[g['id']])),None)
   current=candidate['id'] if candidate else None
   geometry=(self.rects['console'],self.rects[current]) if current else None
   # Align first, then require a deliberate click to press the cartridge home.
   if current!=self.candidate or geometry!=self.last_rect:self.since=now
   self.candidate=current;self.last_rect=geometry
   if self.armed and current!=self.armed:self.armed=None;self.status='INSERT A CARTRIDGE'
   if current and not self.armed and now-self.since>.2:
    self.position(current,seat_rect(self.rects['console'],self.rects[current]))
    self.armed=current;self.status='CLICK CARTRIDGE TO SEAT'
    logging.info('Cartridge aligned: %s',current)
   return True
  except Exception as e:
   logging.exception('Launcher update failed');print(f'Console: {e}',flush=True);self.close('update error');return False
 def launch(self,game):
  logging.info('Launching %s',game['id'])
  logpath=Path(os.environ.get('XDG_CACHE_HOME',Path.home()/'.cache'))/'hyprsplitter'
  logpath.mkdir(parents=True,exist_ok=True)
  self.log=(logpath/f"{game['id']}.log").open('w')
  try:self.child=subprocess.Popen(game['command'],cwd=ROOT,stdout=self.log,stderr=subprocess.STDOUT,env={**os.environ,'GDK_BACKEND':'wayland'})
  except OSError as e:
   self.log.write(str(e));self.log.close();self.log=None;self.status='START FAILED / SEE LOG';self.reset_pending=True;self.inserting=None
  # Keep the seated pose throughout startup and play, until the game exits.
  self.candidate=None;self.armed=None
  for w in self.windows.values():w.set_opacity(1)
 def animate(self):
  if self.closed:return False
  if self.visible:
   for w in self.windows.values():w.queue_draw()
  return True
 def draw(self,area,c,role):
  a=area.get_allocation();t=time.monotonic();game=next((g for g in GAMES if g['id']==self.candidate),None)
  age=t-self.inserting[1] if self.inserting else -1
  if role=='console':
   if self.inserting:game=self.inserting[0]
   c.save();c.translate(0,kick(age)*a.height/360)
   console(c,a.width,a.height,t,game,1 if self.armed else 0,self.status,max(0,age/DURATION))
   c.restore()
  else:
   c.set_operator(cairo.OPERATOR_CLEAR);c.paint();c.set_operator(cairo.OPERATOR_OVER)
   c.save()
   if self.inserting and self.inserting[0]['id']==role:
    c.translate(0,travel(age)*a.height/250)
   cartridge(c,a.width,a.height,next(g for g in GAMES if g['id']==role),t,self.candidate==role)
   c.restore()

 def close(self,reason='shutdown signal or cleanup'):
  if self.closed:return False
  logging.info('Closing launcher: %s',reason)
  self.closed=True
  if self.child and self.child.poll() is None:self.child.terminate()
  if self.log:self.log.close()
  for w in self.windows.values():w.destroy()
  try:
   self.hypr.request(f'eval {self.rule}:set_enabled(false); {self.rule}=nil')
   if self.hypr.request('activeworkspace',True)['id']==self.workspace:self.hypr.run(f'hl.dsp.focus({{workspace={json.dumps(self.previous)}}})')
  except Exception:pass
  if Gtk.main_level():Gtk.main_quit()
  return False

if __name__=='__main__':
 app=Launcher()
 print(f'CONSOLE READY workspace={app.workspace}',flush=True)
 try:Gtk.main()
 finally:app.close()

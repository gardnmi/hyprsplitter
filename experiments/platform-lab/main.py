#!/usr/bin/env python3
"""Real windows become bridges, lifts, stepping stones and puzzle switches."""
import argparse,json,math,os,signal,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from hyprsplitter import Hyprland
from physics import Walker,neighbor,ground,FLOOR
from experiments.surfaces import height as surface_height, slope as surface_slope
from experiments.theme import rgb, FONT
from experiments.visuals import terrain, ellipse
from experiments.rally import quattro as paint_walker, portal
import gi
gi.require_version('Gtk','3.0');gi.require_version('Gdk','3.0');gi.require_version('GLibUnix','2.0')
from gi.repository import Gtk,Gdk,GLib,GLibUnix
import cairo

DEMOS=[
 ('Build a bridge','A adds a floating platform. Drag it into the gap, then Space.'),
 ('Move the bridge','Drag the platform between the ledges. Keep driving while you move it.'),
 ('Widen the bridge','Drag the right edge or use Super + right-drag to span the gap.'),
 ('Split the route','S splits the platform into two windows. Position both pieces.'),
 ('Ride the lift','Board the platform, then drag it up to the exit while driving.'),
 ('Open the passage','Focus the red blocker; Super + W closes it to clear the bridge.'),
 ('Hold the door','Drag the floating weight over the gold pad above the platform.'),
 ('Sticky mud','Mud slows the car. Move it to change the route.'),
 ('Fast lane','Blue arrows accelerate the car. Give it a safe runway.'),
 ('Rolling hill','Drive up the grassy slope and down the other side.'),
 ('Terrain mix','Mud, a hill and a fast lane. Rearrange the windows and try the route.'),
 ('Water crossing','Wade through the waves. Move the water to catch the car.'),
]
TERRAIN={'start','goal','bridge','piece2','piece3','void','dock','blocker','pad'}



def text(c,s,x,y,size=14,color=None):
 c.set_source_rgb(*(color or rgb('foreground')));c.select_font_face(FONT,0,0);c.set_font_size(size);c.move_to(x,y);c.show_text(s)


def line(c,points,color=(.45,.8,.9),width=4):
 c.set_source_rgb(*color);c.set_line_width(width);c.set_line_cap(cairo.LINE_CAP_ROUND);c.move_to(*points[0])
 for p in points[1:]:c.line_to(*p)
 c.stroke()


class Playground:
 def __init__(self,index,state_file):
  self.hypr=Hyprland();self.index=index;self.state_file=state_file
  self.prefix=f'PlatformLab-{os.getpid()}';self.rule=f'platform_lab_{os.getpid()}'
  self.windows={};self.areas={};self.clients={};self.desired={};self.pending=set();self.closed=False;self.error=None
  self.previous=self.hypr.request('activeworkspace',True)['name']
  used={w['id'] for w in self.hypr.request('workspaces',True)}
  self.workspace=next(i for i in range(2,10000) if i not in used)
  m=next(m for m in self.hypr.request('monitors',True) if m['focused'])
  self.mx,self.my=m['x'],m['y'];self.mw,self.mh=m['width']/m['scale'],m['height']/m['scale']
  self.unit=min(1.,(self.mw-70)/1120)
  self.left=int(self.mx+(self.mw-1100*self.unit)/2);self.base=int(self.my+self.mh*.55)
  self.last=time.monotonic();self.started=self.last;self.visible=False
  self.hypr.request(f'eval {self.rule}=hl.window_rule({{name="{self.rule}",match={{initial_title="^{self.prefix}-.*-(start|goal|bridge|piece2|piece3|void|dock|blocker|pad)$"}},workspace="{self.workspace}",float=true,no_anim=true,rounding=0,opacity="1 override 1 override"}})')
  try:
   self.hypr.request(f'eval {self.rule}_tools=hl.window_rule({{name="{self.rule}_tools",match={{initial_title="^{self.prefix}-.*-(hud|weight|air)$"}},workspace="{self.workspace}",float=true,no_anim=true,rounding=0,opacity="1 override 1 override"}})')
   self.hypr.request(f'eval {self.rule}_air=hl.window_rule({{name="{self.rule}_air",match={{initial_title="^{self.prefix}-.*-air$"}},float=true,border_size=0,rounding=0,no_anim=true,no_blur=true,no_shadow=true,no_focus=true}})')
   self.hypr.run(f'hl.dsp.focus({{workspace="{self.workspace}"}})');self.build()
   GLib.timeout_add(60,self.sync);GLib.timeout_add(33,self.tick)
   GLibUnix.signal_add(GLib.PRIORITY_DEFAULT,signal.SIGTERM,self.close)
   GLibUnix.signal_add(GLib.PRIORITY_DEFAULT,signal.SIGINT,self.close)
  except BaseException:self.close();raise

 def rect(self,x,y,w,h=300):
  return (int(self.left+x*self.unit),int(self.base+y),int(w*self.unit),h)

 def build(self):
  for w in self.windows.values():w.destroy()
  self.windows={};self.areas={};self.clients={};self.desired={};self.pending=set()
  self.brand='windows' if self.index%2==0 else 'apple'
  self.walker=Walker();self.placed=False;self.split=False;self.generation=getattr(self,'generation',0)+1
  self.gait=0.;self.landing=0.;self.lean=0.;self.last_geometry={};self.settle_until=0
  self.retire=None;self.setup_current=None
  self.add('hud',(self.left,int(self.my+55),int(1100*self.unit),125))
  self.add('air',(int(self.mx),int(self.my),int(self.mw),int(self.mh)))
  self.add('start',self.rect(0,0,220))
  self.add('goal',self.rect(880,-185 if self.index==4 else 0,220))
  if self.index==0:pass
  elif self.index in (1,3):self.add('bridge',self.rect(230,-330,640))
  elif self.index==2:self.add('bridge',self.rect(230,0,230))
  elif self.index==4:self.add('bridge',self.rect(230,0,640))
  elif self.index==5:
   self.add('bridge',self.rect(230,0,640));self.add('blocker',self.rect(510,-15,160,320))
  elif self.index==6:
   self.add('bridge',self.rect(230,0,640));self.add('pad',self.rect(880,-230,180,120));self.add('weight',self.rect(240,-230,140,100))
  elif self.index==10:
   self.add('bridge',self.rect(230,0,200));self.add('piece3',self.rect(440,0,210));self.add('piece2',self.rect(660,0,210))
  else:self.add('bridge',self.rect(230,0,640))
  self.created=time.monotonic()

 def setup(self):
  if self.pending:return
  if not self.placed:
   self.placed=True;self.hypr.focus(self.clients['start']['address'])
   print(f'READY workspace={self.workspace} demo={self.index+1} {DEMOS[self.index][0]} (floating)',flush=True)

 def remove(self,role):
  self.windows.pop(role).destroy();self.areas.pop(role);self.clients.pop(role,None)
  self.desired.pop(role,None);self.pending.discard(role)

 def title(self,role):return f'{self.prefix}-{self.generation}-{role}'

 def add(self,role,rect):
  self.created=time.monotonic()
  self.desired[role]=rect;self.pending.add(role)
  win=Gtk.Window(title=self.title(role));win.set_decorated(False);win.set_default_size(rect[2],rect[3])
  if role=='air':
   win.set_app_paintable(True);win.set_accept_focus(False);win.set_focus_on_map(False)
   visual=win.get_screen().get_rgba_visual()
   if visual:win.set_visual(visual)
   win.connect('realize',lambda widget:widget.get_window().input_shape_combine_region(cairo.Region(),0,0))
  win.connect('delete-event',self.delete,role);win.connect('key-press-event',self.key)
  area=Gtk.DrawingArea();area.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
  area.connect('button-press-event',self.press,role);area.connect('draw',self.draw,role)
  win.add(area);self.windows[role]=win;self.areas[role]=area;win.show_all()

 def delete(self,win,event,role):
  if role=='blocker':
   self.remove(role)
  else:self.close()
  return True

 def action(self,key):
  if key=='escape':self.close()
  elif key=='b':self.brand='apple' if self.brand=='windows' else 'windows'
  elif key=='n':self.index=(self.index+1)%len(DEMOS);self.build()
  elif key=='p':self.index=(self.index-1)%len(DEMOS);self.build()
  elif key=='r':self.build()
  elif key=='space' and not self.walker.dead:self.walker.running=not self.walker.running
  elif key=='a' and self.index==0 and 'bridge' not in self.windows:
   self.add('bridge',self.rect(230,-330,640))
  elif key=='s' and self.index==3 and not self.split and self.placed:
   r=self.clients.get('bridge')
   if not r:return
   x,y=r['at'];w,h=r['size'];half=(w-12)//2
   self.desired['bridge']=(x,y,half,h);self.position('bridge',self.desired['bridge'])
   self.add('piece2',(x+half+12,y,half,h));self.split=True

 def key(self,win,event):self.action(Gdk.keyval_name(event.keyval).lower());return True

 def press(self,area,event,role):
  if event.button!=1:return False
  if role=='hud' and event.y>78:
   slots=['p','space','r','a' if self.index==0 else 's' if self.index==3 else 'space','n']
   self.action(slots[min(4,int(event.x/area.get_allocated_width()*5))])
  elif role!='air':
   if role in TERRAIN and event.x>area.get_allocated_width()-18:
    self.windows[role].begin_resize_drag(Gdk.WindowEdge.EAST,1,int(event.x_root),int(event.y_root),event.time)
   else:self.windows[role].begin_move_drag(1,int(event.x_root),int(event.y_root),event.time)
  return True

 def position(self,role,rect):
  x,y,w,h=rect;sel=json.dumps('address:'+self.clients[role]['address'])
  self.hypr.run(f'hl.dsp.window.resize({{window={sel},x={w},y={h}}})',f'hl.dsp.window.move({{window={sel},x={x},y={y}}})')

 def geometry(self):
  return {r:tuple(c['at']+c['size']) for r,c in self.clients.items() if c and r in ('start','goal','bridge','piece2','piece3')}

 def surfaces(self):
  if self.index==11:return {'bridge':'water'}
  if self.index==7:return {'bridge':'mud'}
  if self.index==8:return {'bridge':'fast'}
  if self.index==9:return {'bridge':'hill'}
  if self.index==10:return {'bridge':'mud','piece3':'hill','piece2':'fast'}
  return {}

 def exit_open(self):
  if self.index==3:return {'bridge','piece2'}<=self.walker.visited
  if self.index==2:
   bridge=self.clients.get('bridge')
   return bool(bridge and bridge['size'][0]>=self.mw*.30)
  if self.index==6:
   a=self.clients.get('pad');b=self.clients.get('weight')
   if not a or not b:return False
   return a['at'][0]<=b['at'][0]+b['size'][0]/2<=a['at'][0]+a['size'][0] and a['at'][1]<=b['at'][1]+b['size'][1]/2<=a['at'][1]+a['size'][1]
  return True

 def sync(self):
  if self.closed:return False
  try:
   allclients=self.hypr.request('clients',True)
   self.clients={r:next((c for c in allclients if c.get('initialTitle')==self.title(r)),None) for r in self.windows}
   for role in list(self.clients):
    c=self.clients[role]
    if not c:
     if role in self.pending:
      if time.monotonic()-self.created>12:raise RuntimeError('Window creation timed out')
      return True
     raise RuntimeError('A puzzle window disappeared')
    if role in ('hud','air') and not c['floating']:
     # Utility windows must never consume a dwindle slot. Correct float state
     # before moving/resizing, which would otherwise resize the tiling tree.
     sel=json.dumps('address:'+c['address'])
     self.hypr.run(f'hl.dsp.window.float({{window={sel},action="on"}})')
     return True
    if role in self.pending:
     self.position(role,self.desired[role])
     self.pending.remove(role)
    elif role=='air' and tuple(c['at']+c['size'])!=self.desired[role]:self.position(role,self.desired[role])
   if not self.placed:
    self.setup()
    return True
   geometry=self.geometry()
   if geometry!=self.last_geometry:
    previous=self.last_geometry.get(self.walker.room)
    current=geometry.get(self.walker.room)
    if previous and current:self.lean=max(-.15,min(.15,(current[0]-previous[0])*.006))
    self.last_geometry=geometry
   self.visible=self.hypr.request('activeworkspace',True)['id']==self.workspace and all(c['workspace']['id']==self.workspace for c in self.clients.values())
   if self.state_file:
    state={'pid':os.getpid(),'workspace':self.workspace,'demo':self.index+1,'room':self.walker.room,'x':self.walker.x,'running':self.walker.running,'won':self.walker.won,'waiting':self.walker.waiting,'falling':self.walker.falling,'dead':self.walker.dead,'world':[self.walker.world_x,self.walker.world_y],'speed':self.walker.speed,'surfaces':self.surfaces(),'visited':sorted(self.walker.visited),'exit_open':self.exit_open(),'windows':{r:{k:c[k] for k in ('address','at','size','floating')} for r,c in self.clients.items()}}
    tmp=self.state_file.with_suffix('.tmp');tmp.write_text(json.dumps(state));tmp.replace(self.state_file)
  except Exception as e:self.error=str(e);print(f'ERROR: {e}',flush=True);self.close();return False
  return True

 def tick(self):
  if self.closed:return False
  now=time.monotonic();dt=min(.1,now-self.last);self.last=now
  if self.placed and not self.pending and self.visible:
   blocker=self.clients.get('blocker');block=tuple(blocker['at']+blocker['size']) if blocker else None
   was_falling=self.walker.falling
   self.walker.step(dt,self.geometry(),self.exit_open(),block,self.my+self.mh,self.surfaces())
   if was_falling and not self.walker.falling:self.landing=1.
   if self.walker.running and not self.walker.waiting:self.gait+=dt*9*self.walker.speed/90
  self.landing=max(0,self.landing-dt*3);self.lean*=.86
  for a in self.areas.values():a.queue_draw()
  return True

 def draw(self,area,c,role):
  w,h=area.get_allocated_width(),area.get_allocated_height();t=time.monotonic()-self.started
  if role=='air':
   c.set_operator(cairo.OPERATOR_SOURCE);c.set_source_rgba(0,0,0,0);c.paint();c.set_operator(cairo.OPERATOR_OVER)
   if self.walker.falling and not self.walker.dead:
    self.draw_walker(c,self.walker.world_x-self.mx,self.walker.world_y-self.my,t,True)
   return False
  colors={'start':(.09,.17,.22),'goal':(.07,.21,.16),'hud':(.055,.085,.13),'blocker':(.38,.10,.11),'pad':(.28,.21,.08),'weight':(.20,.23,.29)}
  geo=self.geometry();connected=neighbor(role,geo,self.surfaces()) if role in geo else None
  terrain(c,w,h,t,'void' if role in ('void','dock') else self.surfaces().get(role,role), bool(connected) or role=='goal')
  if role=='hud':
   text(c,f'road to omarchy  ::  {self.index+1:02}/{len(DEMOS)}  ::  {DEMOS[self.index][0].lower()}',18,28,17)
   text(c,DEMOS[self.index][1],18,53,14)
   status='[ failed ] R to retry' if self.walker.dead else '[ falling ]' if self.walker.falling else '[ home ]' if self.walker.won else '[ waiting ]' if self.walker.waiting else '[ driving ]' if self.walker.running else '[ paused ] arrange windows, then Space'
   text(c,status,18,77,12,rgb('red') if self.walker.dead else rgb('green'))
   line(c,[(18,88),(w-18,88)],rgb('muted'),1)
   labels=['[P] PREV','[SPACE] DRIVE/PAUSE','[R] RESET','[A] ADD WINDOW' if self.index==0 else '[S] SPLIT' if self.index==3 else '[SPACE] PAUSE','[N] NEXT']
   for i,s in enumerate(labels):text(c,s,18+i*w/5,104,12)
   return False
  if role in ('void','dock'):
   return False
  if role=='blocker':
   for x in range(-h,int(w),45):line(c,[(x,0),(x+h,h)],rgb('red'),12)
   text(c,'CLOSE ME',18,60,18);text(c,'Super + W',18,86,13);return False
  if role in ('pad','weight'):
   if role=='pad':text(c,'PRESSURE PAD',12,30,12);text(c,'DOOR OPEN' if self.exit_open() else 'DOOR LOCKED',12,67,12)
   else:text(c,'WEIGHT',22,38,17);text(c,'Drag onto pad',12,68,12)
   return False
  floor=h-FLOOR;geo=self.geometry();next_room=neighbor(role,geo,self.surfaces()) if role in geo else None
  title={'start':f'LEAVING {self.brand.upper()}','goal':'OMARCHY','bridge':'LIFT' if self.index==4 else 'PLATFORM','piece2':'STEP 2'}.get(role,role)
  title={'mud':'STICKY MUD  /  0.42x','fast':'FAST LANE  /  1.8x','hill':'GRASSY HILL','water':'WATER'}.get(self.surfaces().get(role),title)
  text(c,title.lower(),14,23,12,rgb('foreground'))
  if role in ('start','goal'):
   portal(c,w,floor,t,self.brand if role=='start' else 'omarchy',role=='goal' and not self.exit_open())
   if role=='start':text(c,'[B] switch OS',14,48,10,rgb('muted'))
  elif role not in ('start',):
   if w>320:text(c,':: drag / resize',14,h-12,10,rgb('muted'))
   if self.index==2 and role=='bridge':
    text(c,f'Width {w} / {int(self.mw*.30)} needed',20,60,14)
  if self.walker.falling and not self.walker.dead and role in self.clients:
   origin=self.clients[role]['at']
   self.draw_walker(c,self.walker.world_x-origin[0],self.walker.world_y-origin[1],t,True)
  if role==self.walker.room:
   # Emerge from the source logo and dissolve into Omarchy at the finish.
   opacity=1.
   if role=='start':opacity=max(.15,min(1.,(self.walker.x-28)/75))
   elif role=='goal' and self.exit_open():opacity=max(0.,min(1.,(w*.72-self.walker.x)/(w*.24)))
   c.push_group()
   self.draw_walker(c,self.walker.x,surface_height(w,h,self.walker.x,self.surfaces().get(role,'flat')),t)
   c.pop_group_to_source();c.paint_with_alpha(opacity)
  return False

 def walker_slope(self):
  r=self.geometry().get(self.walker.room)
  return surface_slope(r[2],r[3],self.walker.x,self.surfaces().get(self.walker.room,'flat')) if r else 0

 def draw_walker(self,c,x,floor,t,falling=False):
  c.save();c.translate(x,floor);c.scale(1.,1.)
  paint_walker(c,0,0,t,walking=self.walker.running and not self.walker.waiting,
               falling=falling,happy=self.walker.won,lean=self.lean+math.atan(self.walker_slope()),landing=self.landing,phase=self.gait)
  c.restore()

 def close(self):
  if self.closed:return False
  self.closed=True
  try:restore=self.hypr.request('activeworkspace',True)['id']==self.workspace
  except Exception:restore=False
  for w in self.windows.values():w.destroy()
  try:
   self.hypr.request(f'eval if {self.rule}_tools then {self.rule}_tools:set_enabled(false); {self.rule}_tools=nil end')
   self.hypr.request(f'eval if {self.rule}_air then {self.rule}_air:set_enabled(false); {self.rule}_air=nil end')
   self.hypr.request(f'eval if {self.rule} then {self.rule}:set_enabled(false); {self.rule}=nil end')
  except Exception:pass
  if restore:
   try:self.hypr.run(f'hl.dsp.focus({{workspace={json.dumps(self.previous)}}})')
   except Exception:pass
  if Gtk.main_level():Gtk.main_quit()
  return False


def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--demo',type=int,choices=range(1,len(DEMOS)+1),default=1);p.add_argument('--state-file',type=Path);a=p.parse_args()
 GLib.set_prgname('platform-window-lab');app=Playground(a.demo-1,a.state_file)
 try:Gtk.main()
 finally:app.close()
 if app.error:raise SystemExit(app.error)

if __name__=='__main__':main()

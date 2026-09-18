"""A genuinely immovable Wayland layer, isolated from the GTK3 source window."""
from ctypes import CDLL
CDLL('libgtk4-layer-shell.so')
import gi
gi.require_version('Gtk','4.0');gi.require_version('Gdk','4.0');gi.require_version('Gtk4LayerShell','1.0')
from gi.repository import Gtk,Gdk,GLib,Gtk4LayerShell as Layer
import sys,json,time,os
from pathlib import Path
from types import SimpleNamespace
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from scene import draw_hazard,lemur,portal_art,catcher_art,draw_routes,goal_art,draw_splats,barrier_art,source_art
import cairo
from barrier import Barrier

state_path=Path(sys.argv[1]);parent=int(sys.argv[2]);connector=sys.argv[3];top=int(sys.argv[4]);started=time.monotonic()
class Panel(Gtk.Application):
 def do_activate(self):
  self.data={};self.window=Gtk.Window(application=self);self.window.set_decorated(False);self.window.set_default_size(1,82)
  Layer.init_for_window(self.window);Layer.set_namespace(self.window,'lemur-suppression')
  Layer.set_layer(self.window,Layer.Layer.BOTTOM);Layer.set_keyboard_mode(self.window,Layer.KeyboardMode.NONE)
  Layer.set_exclusive_zone(self.window,-1)
  monitors=Gdk.Display.get_default().get_monitors()
  for i in range(monitors.get_n_items()):
   m=monitors.get_item(i)
   if m.get_connector()==connector:Layer.set_monitor(self.window,m);self.monitor=m;break
  for edge in (Layer.Edge.TOP,Layer.Edge.LEFT,Layer.Edge.RIGHT):Layer.set_anchor(self.window,edge,True)
  Layer.set_margin(self.window,Layer.Edge.TOP,top)
  self.window.connect('realize',lambda win:win.get_surface().set_input_region(cairo.Region()))
  self.area=Gtk.DrawingArea();self.area.set_content_height(82);self.area.set_draw_func(self.draw);self.window.set_child(self.area)
  self.catch=Gtk.Window(application=self);self.catch.set_decorated(False);self.catch.set_default_size(230,210)
  Layer.init_for_window(self.catch);Layer.set_namespace(self.catch,'lemur-catcher');Layer.set_layer(self.catch,Layer.Layer.BOTTOM)
  Layer.set_keyboard_mode(self.catch,Layer.KeyboardMode.NONE);Layer.set_exclusive_zone(self.catch,-1)
  if hasattr(self,'monitor'):Layer.set_monitor(self.catch,self.monitor)
  Layer.set_anchor(self.catch,Layer.Edge.TOP,True);Layer.set_anchor(self.catch,Layer.Edge.LEFT,True)
  self.catcharea=Gtk.DrawingArea();self.catcharea.set_draw_func(self.draw_catcher);self.catch.set_child(self.catcharea)
  self.goal=Gtk.Window(application=self);self.goal.set_decorated(False);self.goal.set_default_size(400,210)
  Layer.init_for_window(self.goal);Layer.set_namespace(self.goal,'lemur-omacon');Layer.set_layer(self.goal,Layer.Layer.BOTTOM)
  Layer.set_keyboard_mode(self.goal,Layer.KeyboardMode.NONE);Layer.set_exclusive_zone(self.goal,-1)
  if hasattr(self,'monitor'):Layer.set_monitor(self.goal,self.monitor)
  Layer.set_anchor(self.goal,Layer.Edge.TOP,True);Layer.set_anchor(self.goal,Layer.Edge.LEFT,True)
  self.goalarea=Gtk.DrawingArea();self.goalarea.set_draw_func(self.draw_goal);self.goal.set_child(self.goalarea)
  self.gates={}
  for role in ('gate','apple_gate','source','elevator'):
   win=Gtk.Window(application=self);win.set_decorated(False)
   Layer.init_for_window(win);Layer.set_namespace(win,'lemur-'+role);Layer.set_layer(win,Layer.Layer.BOTTOM)
   Layer.set_keyboard_mode(win,Layer.KeyboardMode.NONE);Layer.set_exclusive_zone(win,-1)
   if hasattr(self,'monitor'):Layer.set_monitor(win,self.monitor)
   Layer.set_anchor(win,Layer.Edge.TOP,True);Layer.set_anchor(win,Layer.Edge.LEFT,True)
   if role=='elevator':
    css=Gtk.CssProvider();css.load_from_data(b'window, drawingarea { background-color: transparent; }');win.get_style_context().add_provider(css,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
   if role!='source':win.connect('realize',lambda widget:widget.get_surface().set_input_region(cairo.Region()))
   area=Gtk.DrawingArea();area.set_draw_func(self.draw_gate,role);win.set_child(area);self.gates[role]=(win,area)
   if role=='source':
    Layer.set_keyboard_mode(win,Layer.KeyboardMode.ON_DEMAND)
    click=Gtk.GestureClick.new();click.connect('released',lambda *_:self.command('space'));area.add_controller(click)
    keys=Gtk.EventControllerKey.new();keys.connect('key-pressed',self.source_key);win.add_controller(keys)
  self.rotation=0.;self.seq=0
  drag=Gtk.GestureDrag.new();drag.connect('drag-begin',self.begin_rotate);drag.connect('drag-update',self.rotate)
  self.catcharea.add_controller(drag)
  scroll=Gtk.EventControllerScroll.new(Gtk.EventControllerScrollFlags.VERTICAL);scroll.connect('scroll',self.scroll_rotate);self.catcharea.add_controller(scroll)
  self.hold();GLib.timeout_add(16,self.tick)
 def command(self,key):
  path=state_path.with_suffix('.control');tmp=path.with_suffix('.control.tmp');tmp.write_text(key);tmp.replace(path)
 def source_key(self,controller,keyval,keycode,state):
  key=Gdk.keyval_name(keyval).lower()
  if key in ('space','r','escape'):self.command(key);return True
  return False
 def send_rotation(self,value):
  import math
  self.rotation=max(-math.pi,min(0,value));self.seq+=1
  path=state_path.with_suffix('.input');tmp=path.with_suffix('.input.tmp')
  tmp.write_text(json.dumps({'seq':self.seq,'angle':self.rotation}));tmp.replace(path)
 def begin_rotate(self,gesture,x,y):
  self.drag_angle=self.data.get('catcher_angle',0)
 def rotate(self,gesture,dx,dy):
  self.send_rotation(self.drag_angle+(dx-dy)*.014)
 def scroll_rotate(self,controller,dx,dy):
  self.send_rotation(self.rotation-dy*.20);return True
 def tick(self):
  if not Path(f'/proc/{parent}').exists():self.quit();return False
  try:self.data=json.loads(state_path.read_text())
  except (OSError,ValueError):return True
  visible=self.data.get('visible',False)
  self.window.set_visible(visible)
  if 'catcher' in self.data:
   x,y,w,h=self.data['catcher'];hx,hy,_,_=self.data['hazard']
   Layer.set_margin(self.catch,Layer.Edge.LEFT,int(x-hx));Layer.set_margin(self.catch,Layer.Edge.TOP,int(y-(hy-top)))
   self.catch.set_visible(visible)
   if visible:self.catcharea.queue_draw()
  if 'goal' in self.data:
   x,y,w,h=self.data['goal'];hx,hy,_,_=self.data['hazard']
   Layer.set_margin(self.goal,Layer.Edge.LEFT,int(x-hx));Layer.set_margin(self.goal,Layer.Edge.TOP,int(y-(hy-top)))
   self.goal.set_visible(visible)
   if visible:self.goalarea.queue_draw()
  for role,(win,area) in self.gates.items():
   if role not in self.data:continue
   x,y,w,h=self.data[role];hx,hy,_,_=self.data['hazard']
   win.set_default_size(int(w),int(h));area.set_content_width(int(w));area.set_content_height(int(h))
   Layer.set_margin(win,Layer.Edge.LEFT,int(x-hx));Layer.set_margin(win,Layer.Edge.TOP,int(y-(hy-top)))
   win.set_visible(visible)
   if visible:area.queue_draw()
  if visible:self.area.queue_draw()
  return True
 def draw_gate(self,area,c,w,h,role):
  d=self.data
  if 'barriers' not in d:return
  index=1 if role=='apple_gate' else 0;rect=d[role];ox,oy=rect[:2]
  if role=='source':source_art(c,w,h,d)
  elif role=='elevator':
   from mechanics import Journey
   from journey_art import draw_piece
   journey=Journey.__new__(Journey);journey.rects=d['journey'];journey.progress=d['lift_progress'];journey.docked=set(d['docked'])
   draw_piece(c,w,h,role,journey,None,time.monotonic()-started)
  else:
   barrier=Barrier();barrier.__dict__.update(d['barriers'][index]);barrier_art(c,w,h,barrier,rect,index==1)
  draw_routes(c,d.get('routes',[]),(ox,oy),time.monotonic()-started)
  for i,a in enumerate(d['lemurs']):
   if a['state'] not in ('lost','saved'):lemur(c,a['x']-ox,a['y']-oy,d['time'],a['state']=='fall',i*.71,-1 if a['speed']<0 else 1,slide=a['room']==2,ride=a['room']==1,tilt=a.get('tilt',0))
  draw_splats(c,d['splats'],d['effect_time'],(ox,oy))
 def draw_goal(self,area,c,w,h):
  goal_art(c,w,h,self.data)
  if 'goal' in self.data:draw_splats(c,self.data.get('splats',[]),self.data.get('effect_time',0),self.data['goal'][:2])
 def draw_catcher(self,area,c,w,h):
  d=self.data
  if 'catcher' not in d:return
  ox,oy=d['catcher'][:2];t=time.monotonic()-started
  catcher_art(c,w,h,t,d.get('catcher_angle',0));draw_routes(c,d.get('routes',[]),(ox,oy),t)
  for i,a in enumerate(d['lemurs']):
   if a['state'] not in ('lost','saved'):lemur(c,a['x']-ox,a['y']-oy,d['time'],a['state']=='fall',i*.71,-1 if a['speed']<0 else 1,slide=a['room']==2,ride=a['room']==1,tilt=a.get('tilt',0))
  draw_splats(c,d['splats'],d['effect_time'],(ox,oy))
 def draw(self,area,c,w,h):
  d=self.data
  if 'hazard' not in d:return
  ctx=SimpleNamespace(hazard=d['hazard'],routes=d.get('routes',[]),colony=SimpleNamespace(shot=d['shot'],splats=d['splats'],effect_time=d['effect_time']))
  draw_hazard(ctx,c,w,h,time.monotonic()-started)
  ox,oy=d['hazard'][:2]
  for i,a in enumerate(d['lemurs']):
   if a['state'] not in ('lost','saved'):lemur(c,a['x']-ox,a['y']-oy,d['time'],a['state']=='fall',i*.71,-1 if a['speed']<0 else 1,slide=a['room']==2,ride=a['room']==1,tilt=a.get('tilt',0))
Panel(application_id=f'org.hyprsplitter.Hazard{parent}').run([])

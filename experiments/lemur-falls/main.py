#!/usr/bin/env python3
"""Road to OMACON: a window-to-window puzzle starring Tux."""
import json,math,os,signal,sys,time,subprocess
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from hyprsplitter import Hyprland
from style import rgb,panel,heading,hint
from model import Colony
from barrier import Barrier
from mechanics import Journey
from layout import arrange,objective
from saver import Saver
from hazard_art import minigun,MUZZLE_X,BEAM_HALF_HEIGHT
import tempfile
import gi
for name,version in [('Gtk','3.0'),('Gdk','3.0'),('GLibUnix','2.0')]:gi.require_version(name,version)
from gi.repository import Gtk,Gdk,GLib,GLibUnix
import cairo


from scene import text,lemur,portal_art,draw_routes,catcher_art,draw_splats
from portals import beam_routes,bands

class App:
 def __init__(self):
  self.closed=False;self.hypr=Hyprland();self.rule=f'lemur_falls_{os.getpid()}';self.title=f'LemurFalls-{os.getpid()}'
  self.previous=self.hypr.request('activeworkspace',True)['name'];used={w['id'] for w in self.hypr.request('workspaces',True)};self.workspace=next(i for i in range(2,1000) if i not in used)
  m=next(m for m in self.hypr.request('monitors',True) if m['focused'])
  self.mx,self.my=m['x'],m['y'];self.mw,self.mh=int(m['width']/m['scale']),int(m['height']/m['scale'])
  self.rect=(self.mx+100,self.my+120,600,300);self.placed=False
  self.hazard=(self.mx,self.my+int(self.mh*.36),self.mw,82)
  self.portals=[(self.mx+480,self.my+int(self.mh*.36)+int(82*.47)-75,110,150),(self.mx+1000,self.my+360,110,150)]
  self.catcher=(self.mx+int(self.mw*.16),self.hazard[1]+self.hazard[3]+12,230,210)
  self.goal=(self.mx+self.mw-432,self.my+60,400,210)
  self.barrier=Barrier();self.gate=(self.goal[0]-430,self.goal[1]+30,400,180)
  self.apple_barrier=Barrier();self.apple_gate=(self.gate[0]-430,self.gate[1]+220,400,180)
  self.journey=Journey(self.mx,self.my,self.mw,self.mh,self.goal)
  self.gate=(self.mx+30,self.my+self.mh-300,self.mw*.43,180)
  ex,ey,ew,eh=self.journey.rects['elevator']
  self.apple_gate=(ex+ew,ey+10,self.goal[0]-(ex+ew),180)
  arrange(self)
  self.plugin_starts={role:tuple(self.journey.rects[role]) for role in Journey.roles[:2]}
  self.portal_starts=list(self.portals);self.reset_portals=False
  self.angle=0.;self.target_angle=0.;self.command_seq=0
  self.routes=[];self.intake=None
  self.saver=Saver();self.colony=Colony(total=1);self.last=time.monotonic();self.started=self.last;self.visible=True;self.frame=0
  self.hypr.request(f'eval {self.rule}=hl.window_rule({{name="{self.rule}",match={{initial_title="^{self.title}.*$"}},workspace="{self.workspace}",float=true,no_anim=true,rounding=0,opacity="1 override 1 override"}})')
  self.hypr.request(f'eval {self.rule}_air=hl.window_rule({{name="{self.rule}_air",match={{initial_title="^{self.title}-air$"}},float=true,no_focus=true,no_blur=true,no_shadow=true,border_size=0}})')
  self.hypr.request(f'eval {self.rule}_lift=hl.window_rule({{name="{self.rule}_lift",match={{initial_title="^{self.title}-elevator$"}},no_blur=true,no_shadow=true,border_size=0}})')
  self.hypr.request(f'eval {self.rule}_apple=hl.window_rule({{name="{self.rule}_apple",match={{initial_title="^{self.title}-apple$"}},rounding=20}})')
  self.hypr.run(f'hl.dsp.focus({{workspace="{self.workspace}"}})')
  self.windows={}
  for role in ('air','portal0','portal1')+Journey.roles[:2]:
   win=Gtk.Window(title=self.title+('' if role=='source' else '-'+role));win.set_decorated(False)
   win.set_default_size(*( (self.mw,self.mh) if role=='air' else self.journey.rects[role][2:] if role in Journey.roles else (400,180) if role in ('gate','apple') else (110,150) if role.startswith('portal') else (230,210) if role=='catcher' else (600,300)))
   if role=='hazard':
    win.set_resizable(False);win.set_accept_focus(False);win.set_focus_on_map(False)
    win.connect('realize',lambda widget:widget.get_window().input_shape_combine_region(cairo.Region(),0,0))
   if role in ('air','elevator'):
    win.set_app_paintable(True)
    if role=='air':win.set_accept_focus(False);win.set_focus_on_map(False)
    visual=win.get_screen().get_rgba_visual()
    if visual:win.set_visual(visual)
    if role=='air':win.connect('realize',lambda widget:widget.get_window().input_shape_combine_region(cairo.Region(),0,0))
   if role=='elevator':
    css=Gtk.CssProvider();css.load_from_data(b'window, drawingarea { background-color: transparent; }');win.get_style_context().add_provider(css,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
   win.connect('delete-event',lambda *_:self.close());win.connect('key-press-event',self.key)
   area=Gtk.DrawingArea();area.add_events(Gdk.EventMask.BUTTON_PRESS_MASK|Gdk.EventMask.BUTTON_RELEASE_MASK)
   if role!='air':area.connect('button-press-event',self.drag,win)
   if role in ('plugin2','plugin3'):area.set_tooltip_text('Calendar / Caldir' if role=='plugin2' else 'Stay Awake')
   area.connect('draw',self.draw,role);win.add(area);win.show_all();self.windows[role]=win
  self.layer_runtime=tempfile.TemporaryDirectory(prefix='omatari-tux-')
  self.layer_path=Path(self.layer_runtime.name)/'layer.json'
  self.layer_path.write_text('{}')
  self.layer=subprocess.Popen([sys.executable,str(Path(__file__).with_name('hazard_layer.py')),str(self.layer_path),str(os.getpid()),m['name'],str(self.hazard[1]-self.my)])
  GLib.timeout_add(60,self.sync);GLib.timeout_add(33,self.tick)
  for sig in (signal.SIGTERM,signal.SIGINT):GLibUnix.signal_add(GLib.PRIORITY_DEFAULT,sig,self.close)
 def drag(self,a,e,win):
  if e.button==1:win.begin_move_drag(1,int(e.x_root),int(e.y_root),e.time)
  return True
 def key(self,w,e):
  return self.action(Gdk.keyval_name(e.keyval).lower())
 def action(self,k):
  if k=='escape':self.close()
  elif k=='r':self.colony=Colony(total=1);self.barrier=Barrier();self.apple_barrier=Barrier();self.journey.reset();self.journey.rects.update(self.plugin_starts);self.angle=0.;self.target_angle=0.;self.reset_portals=True
  elif k=='space' and self.colony.saved+self.colony.lost<self.colony.total:self.colony.running=not self.colony.running
  return True
 def position(self,client,rect):
  x,y,w,h=rect;sel=json.dumps('address:'+client['address'])
  self.hypr.run(f'hl.dsp.window.resize({{window={sel},x={w},y={h}}})',f'hl.dsp.window.move({{window={sel},x={x},y={y}}})')
 def sync(self):
  if self.closed:return False
  try:
   clients=self.hypr.request('clients',True)
   air=next((c for c in clients if c.get('initialTitle')==self.title+'-air'),None)
   portals=[next((c for c in clients if c.get('initialTitle')==self.title+f'-portal{i}'),None) for i in range(2)]
   extras={role:next((c for c in clients if c.get('initialTitle')==self.title+'-'+role),None) for role in Journey.roles[:2]}
   if not all(extras.values()) or not air or not all(portals):
    if self.placed or time.monotonic()-self.started>10:self.close();return False
    return True
   if not self.placed:
    for role,client in extras.items():self.position(client,self.journey.rects[role])
    self.position(air,(self.mx,self.my,self.mw,self.mh))
    for i,p in enumerate(portals):self.position(p,self.portals[i])
    self.hypr.focus(portals[0]['address']);self.placed=True
    print(f'READY workspace={self.workspace}: source + minigun barrier. Space releases the colony.',flush=True)
    return True
   if not air['floating']:
    sel=json.dumps('address:'+air['address']);self.hypr.run(f'hl.dsp.window.float({{window={sel},action="on"}})')
   if tuple(air['at']+air['size'])!=(self.mx,self.my,self.mw,self.mh):self.position(air,(self.mx,self.my,self.mw,self.mh))
   for role,client in extras.items():
    if self.reset_portals:
     self.position(client,self.plugin_starts[role])
     self.journey.rects[role]=self.plugin_starts[role]
     continue
    newrect=tuple(client['at']+client['size']);oldrect=self.journey.rects[role]
    index=3 if role=='elevator' else -1
    for a in self.colony.lemurs:
     if a.room==index:a.x+=newrect[0]-oldrect[0];a.y+=newrect[1]-oldrect[1]
    self.journey.rects[role]=newrect
   if self.reset_portals:
    for client,rect in zip(portals,self.portal_starts):self.position(client,rect)
    self.portals=list(self.portal_starts);self.reset_portals=False
   else:self.portals=[tuple(p['at']+p['size']) for p in portals]
   self.visible=self.hypr.request('activeworkspace',True)['id']==self.workspace and all(p['workspace']['id']==self.workspace for p in portals) and all(c['workspace']['id']==self.workspace for c in extras.values())
  except Exception as e:print(f'ERROR: {e}',flush=True);self.close();return False
  return True
 def tick(self):
  if self.closed:return False
  now=time.monotonic();dt=min(.05,now-self.last);self.last=now
  try:
   control=self.layer_path.with_suffix('.control')
   if control.exists():
    try:
     command=control.read_text();control.unlink();self.action(command)
    except OSError:pass
    if self.closed:return False
   self.saver.poll()
   if self.layer.poll() is not None:raise RuntimeError('Hazard layer exited')
   if self.visible and self.placed:
    x,y,w,h=self.rect
    self.journey.step(dt if self.colony.running else 0,self.colony)
    self.routes,self.intake=beam_routes(self.hazard,self.portals,MUZZLE_X,BEAM_HALF_HEIGHT)
    self.barrier.step(dt,[],self.gate)
    self.routes=self.apple_barrier.step(dt,self.routes,self.apple_gate)
    command=self.layer_path.with_suffix('.input')
    if command.exists():
     try:
      event=json.loads(command.read_text())
      if event['seq']!=self.command_seq:
       self.command_seq=event['seq'];self.target_angle=max(-math.pi,min(0,event['angle']))
     except (OSError,ValueError,KeyError):pass
    previous=self.angle
    self.angle+=(self.target_angle-self.angle)*min(1,dt*12)
    previous_rooms=[a.room for a in self.colony.lemurs];previous_x=[a.x for a in self.colony.lemurs]
    self.colony.step(dt,[(x,y+h-20,w),(self.gate[0],self.gate[1]+self.gate[3]-20,self.gate[2]),(self.apple_gate[0],self.apple_gate[1]+self.apple_gate[3]-20,self.apple_gate[2])]+self.journey.ledges(),(x+max(24,w*.10),y+h-65),self.my+self.mh,exit_room=None,hazards=bands(self.routes,BEAM_HALF_HEIGHT),portals=self.portals,catcher=(self.catcher,self.angle,previous),goal=self.goal,windows_terrain=self.gate,soft_rooms=tuple(range(1,4)),waiting_rooms=(3,) if self.journey.progress<.999 else (),blockers=[b.rect(r) for b,r in ((self.apple_barrier,self.apple_gate),) if b.health>0])
    self.barrier.rider=any(a.room==1 and a.state=='walk' for a in self.colony.lemurs)
    self.barrier.chair_impact(self.colony.lemurs,self.gate,self.journey.ledges()[0])
    self.apple_barrier.observe_apple(previous_rooms,previous_x,self.colony.lemurs,self.apple_gate)
    for win in self.windows.values():win.queue_draw()
   data={'source':self.rect,'cells':self.saver.cells,'total':self.colony.total,'spawned':self.colony.spawned,'visible':self.visible and self.placed,'hazard':self.hazard,'time':self.colony.time,'effect_time':self.colony.effect_time,'shot':self.colony.shot,'splats':self.colony.splats,'lemurs':[vars(a) for a in self.colony.lemurs],'portals':self.portals,'routes':self.routes,'intake':self.intake,'elevator':self.journey.rects['elevator'],'lift_progress':self.journey.progress,'docked':list(self.journey.docked),'journey':self.journey.rects,'apple_gate':self.apple_gate,'gate':self.gate,'barriers':[vars(self.barrier),vars(self.apple_barrier)],'gate_health':self.barrier.health,'goal':self.goal,'saved':self.colony.saved,'arrivals':self.colony.arrivals,'catcher':self.catcher,'catcher_angle':self.angle}
   tmp=self.layer_path.with_suffix('.tmp');tmp.write_text(json.dumps(data));tmp.replace(self.layer_path)
  except Exception as e:print(f'ERROR: {e}',flush=True);self.close();return False
  return True
 def draw(self,a,c,role):
  w,h=a.get_allocated_width(),a.get_allocated_height();t=time.monotonic()-self.started
  if role in Journey.roles:
   from journey_art import draw_piece
   rect=self.journey.rects[role];ox,oy=rect[:2]
   draw_piece(c,w,h,role,self.journey,self.colony,t)
   draw_routes(c,self.routes,(ox,oy),t)
   for i,animal in enumerate(self.colony.lemurs):
    if animal.state not in ('lost','saved'):lemur(c,animal.x-ox,animal.y-oy,self.colony.time,animal.state=='fall',i*.71,-1 if animal.speed<0 else 1,slide=animal.room==2,ride=animal.room==1,tilt=animal.tilt)
   draw_splats(c,self.colony.splats,self.colony.effect_time,(ox,oy));return False
  if role in ('gate','apple'):
   from scene import barrier_art
   rect=self.apple_gate if role=='apple' else self.gate
   barrier_art(c,w,h,self.apple_barrier if role=='apple' else self.barrier,rect,role=='apple')
   ox,oy=rect[:2];draw_routes(c,self.routes,(ox,oy),t)
   for i,animal in enumerate(self.colony.lemurs):
    if animal.state not in ('lost','saved'):lemur(c,animal.x-ox,animal.y-oy,self.colony.time,animal.state=='fall',i*.71,-1 if animal.speed<0 else 1,slide=animal.room==2,ride=animal.room==1,tilt=animal.tilt)
   draw_splats(c,self.colony.splats,self.colony.effect_time,(ox,oy))
   return False
  if role=='catcher':
   ox,oy=self.catcher[:2];catcher_art(c,w,h,t);draw_routes(c,self.routes,(ox,oy),t)
   for i,animal in enumerate(self.colony.lemurs):
    if animal.state not in ('lost','saved'):lemur(c,animal.x-ox,animal.y-oy,self.colony.time,animal.state=='fall',i*.71,-1 if animal.speed<0 else 1,slide=animal.room==2,ride=animal.room==1,tilt=animal.tilt)
   draw_splats(c,self.colony.splats,self.colony.effect_time,(ox,oy))
   return False
  if role.startswith('portal'):
   index=int(role[-1]);ox,oy=self.portals[index][:2]
   panel(c,w,h,'foreground' if index==0 else 'bright_green')
   draw_routes(c,self.routes,(ox,oy),t)
   portal_art(c,w,h,t,index,self.intake is not None)
   for i,animal in enumerate(self.colony.lemurs):
    if animal.state not in ('lost','saved'):lemur(c,animal.x-ox,animal.y-oy,self.colony.time,animal.state=='fall',i*.71,-1 if animal.speed<0 else 1,slide=animal.room==2,ride=animal.room==1,tilt=animal.tilt)
   draw_splats(c,self.colony.splats,self.colony.effect_time,(ox,oy))
   return False
  if role=='air':
   c.set_operator(cairo.OPERATOR_SOURCE);c.set_source_rgba(0,0,0,0);c.paint();c.set_operator(cairo.OPERATOR_OVER)
   ox,oy=self.mx,self.my
   draw_routes(c,self.routes,(ox,oy),t)
   from layout_art import draw_route
   draw_route(c,self,t)
  else:
   panel(c,w,h,'bright_green');ox,oy=self.rect[:2]
   c.save();c.translate(14,38);c.scale(max(.1,(w-28)/900),max(.1,(h-100)/234))
   c.select_font_face('monospace',0,0);c.set_font_size(16)
   for col,row,ch,color in self.saver.cells:
    c.set_source_rgb(*color);c.move_to(col*10,16+row*13);c.show_text(ch)
   c.restore()
   heading(c,f'TUX / DEPARTURES / {self.colony.total-self.colony.spawned:03} WAITING','foreground')
   c.set_source_rgb(*rgb('dark_background'));c.rectangle(0,h-20,w,20);c.fill()
   c.set_source_rgb(*rgb('cyan'));c.set_line_width(3);c.move_to(0,h-20);c.line_to(w,h-20);c.stroke()
   draw_routes(c,self.routes,(ox,oy),t)
   hint(c,'SPACE start/pause / R reset / ESC close',h)
  for i,animal in enumerate(self.colony.lemurs):
   if animal.state not in ('lost','saved') and (role=='source' or animal.room is None):
    lemur(c,animal.x-ox,animal.y-oy,self.colony.time,animal.state=='fall',i*.71,-1 if animal.speed<0 else 1,slide=animal.room==2,ride=animal.room==1,tilt=animal.tilt)
  if role=='air':
   for x,y,born in self.colony.bursts:
    age=self.colony.time-born
    for i in range(8):
     c.set_source_rgba(*rgb('muted'),max(0,1-age/.7));c.rectangle(x-ox+math.sin(i*2.4)*age*30,y-oy-age*35,2,2);c.fill()
  draw_splats(c,self.colony.splats,self.colony.effect_time,(ox,oy))
  return False
 def close(self):
  if self.closed:return False
  self.closed=True;self.saver.close()
  if hasattr(self,'layer'):
   self.layer.terminate()
   try:self.layer.wait(timeout=2)
   except subprocess.TimeoutExpired:self.layer.kill();self.layer.wait()
   self.layer_path.with_suffix('.control').unlink(missing_ok=True);self.layer_path.with_suffix('.input').unlink(missing_ok=True);self.layer_path.with_suffix('.input.tmp').unlink(missing_ok=True)
   self.layer_path.unlink(missing_ok=True);self.layer_path.with_suffix('.tmp').unlink(missing_ok=True)
   self.layer_runtime.cleanup()
  for win in self.windows.values():win.destroy()
  try:
   self.hypr.request(f'eval {self.rule}_apple:set_enabled(false); {self.rule}_apple=nil; {self.rule}_lift:set_enabled(false); {self.rule}_lift=nil; {self.rule}_air:set_enabled(false); {self.rule}_air=nil; {self.rule}:set_enabled(false); {self.rule}=nil')
   if self.hypr.request('activeworkspace',True)['id']==self.workspace:self.hypr.run(f'hl.dsp.focus({{workspace={json.dumps(self.previous)}}})')
  except Exception:pass
  if Gtk.main_level():Gtk.main_quit()
  return False

if __name__=='__main__':
 app=App()
 try:Gtk.main()
 finally:app.close()

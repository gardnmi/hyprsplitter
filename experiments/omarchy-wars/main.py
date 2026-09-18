#!/usr/bin/env python3
"""Omarchy: Zero Day — an Omatari arena shooter."""
import sys,os,json,time,signal,math,copy
import cairo
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
import gi
gi.require_version('Gtk','3.0');gi.require_version('Gdk','3.0');gi.require_version('GLibUnix','2.0')
from gi.repository import Gtk,Gdk,GLib,GLibUnix
from hyprsplitter import Hyprland
from model import Game,Enemy,W,H
from art import draw,text,glow,enemy_art,pickup_art
from board import Board
from invasion import layout,replacements
from difficulty import settings
from experiments.theme import rgb

class App:
 def __init__(self):
  self.h=Hyprland();self.closed=False;self.game=Game();self.keys=set();self.aim=(W/2+100,H/2);self.shooting=False;self.paused=False
  self.bestpath=Path(os.environ.get('XDG_STATE_HOME',Path.home()/'.local/state'))/'hyprsplitter/zero-day.json'
  try:self.best=max(0,int(json.loads(self.bestpath.read_text())['best']))
  except (OSError,ValueError,KeyError,TypeError):self.best=0
  self.previous=self.h.request('activeworkspace',True)['name'];used={w['id'] for w in self.h.request('workspaces',True)}
  self.workspace=next(i for i in range(2,1000) if i not in used)
  m=next(m for m in self.h.request('monitors',True) if m['focused']);mw,mh=m['width']/m['scale'],m['height']/m['scale'];s=min(1,mw*.88/W,mh*.88/H)
  self.rect=(int(m['x']+(mw-W*s)/2),int(m['y']+(mh-H*s)/2),int(W*s),int(H*s));self.rule=f'zero_day_{os.getpid()}';self.title=f'Omatari-ZeroDay-{os.getpid()}'
  self.h.request(f'eval {self.rule}=hl.window_rule({{name="{self.rule}",match={{initial_title="^{self.title}-.*$"}},workspace="{self.workspace}",float=true,no_anim=true,rounding=0}})')
  self.h.run(f'hl.dsp.focus({{workspace="{self.workspace}"}})')
  self.origin=(m['x'],m['y']);self.world_scale=(W/mw,H/mh)
  home,self.attack_rects,self.tilts=layout(m['x'],m['y'],mw,mh)
  self.starts={'home':home};self.rects=dict(self.starts);self.board=Board(self.world_rects(self.rects),invasion=True);self.game=Game(board=self.board);self.game.spawn=99999
  self.board.angles=self.tilts;self.board.visual_scale=self.world_scale
  self.monitor=(int(m['x']),int(m['y']),int(mw),int(mh));self.pending=set();self.spawned_rooms=set();self.cleared=set();self.attack_clock=0.;self.visual_age={}
  self.windows={};self.areas={};self.visible=True;self.started=time.monotonic();self.placed=False
  self.h.request(f'eval {self.rule}_air=hl.window_rule({{name="{self.rule}_air",match={{initial_title="^{self.title}-air$"}},float=true,no_initial_focus=true,no_blur=true,no_shadow=true,border_size=0,opacity="1 override 1 override"}})')
  self.h.request(f'eval {self.rule}_attacks=hl.window_rule({{name="{self.rule}_attacks",match={{initial_title="^{self.title}-attack.*$"}},no_initial_focus=true,border_size=0,no_blur=true,no_shadow=true,opacity="1 override 1 override"}})')
  self.make_window('air',self.monitor);self.make_window('home',home)
  self.last=time.monotonic()
  GLib.timeout_add(70,self.sync);GLib.timeout_add(16,self.tick)
  for sig in (signal.SIGTERM,signal.SIGINT):GLibUnix.signal_add(GLib.PRIORITY_DEFAULT,sig,self.close)
 def make_window(self,role,rect):
  win=Gtk.Window(title=self.title+'-'+role);win.set_default_size(*rect[2:]);win.set_decorated(False)
  if role=='air' or role.startswith('attack'):
   win.set_app_paintable(True);win.set_accept_focus(True);win.set_focus_on_map(False)
   visual=win.get_screen().get_rgba_visual()
   if visual:win.set_visual(visual)
  win.set_focus_on_map(role=='home')
  win.connect('delete-event',lambda *_:self.close() or True)
  win.connect('key-press-event',self.key);win.connect('key-release-event',self.release)
  win.connect('focus-out-event',self.unfocus)
  area=Gtk.DrawingArea();area.add_events(Gdk.EventMask.POINTER_MOTION_MASK|Gdk.EventMask.BUTTON_PRESS_MASK|Gdk.EventMask.BUTTON_RELEASE_MASK)
  area.connect('motion-notify-event',self.motion,role);area.connect('button-press-event',self.button,role);area.connect('button-release-event',self.button,role)
  area.connect('draw',self.draw_room,role);win.add(area);self.windows[role]=win;self.areas[role]=area;self.pending.add(role);win.show_all()
 def randomize_attack(self,role):
  mx,my,mw,mh=self.monitor;hx,hy,hw,hh=self.rects['home'];rng=self.game.rng
  for _ in range(100):
   w=int(mw*rng.uniform(.15,.26));h=int(mh*rng.uniform(.17,.29))
   x=rng.randint(mx+18,mx+mw-w-18);y=rng.randint(my+45,my+mh-h-18)
   if x+w<hx-15 or x>hx+hw+15 or y+h<hy-15 or y>hy+hh+15:
    self.attack_rects[role]=(x,y,w,h);break
  self.tilts[role]=rng.choice((-1,1))*rng.uniform(.12,.32)
 def open_attack(self,role):
  rect=self.attack_rects[role];self.starts[role]=rect;self.rects[role]=rect;self.board.rects.update(self.world_rects({role:rect}));self.spawned_rooms.add(role);self.visual_age[role]=0.
  self.make_window(role,rect)
 def reset(self):
  self.save()
  for role in list(self.windows):
   if role.startswith('attack'):self.windows.pop(role).destroy();self.areas.pop(role);self.pending.discard(role)
  self.starts={'home':self.rects['home']};self.rects=dict(self.starts);self.board=Board(self.world_rects(self.rects),invasion=True)
  self.game=Game(board=self.board);self.game.state='install';self.game.spawn=99999;self.board.angles=self.tilts;self.board.visual_scale=self.world_scale;self.spawned_rooms.clear();self.cleared.clear();self.attack_clock=0.;self.paused=False;self.shooting=False
 def world_rects(self,rects):
  ox,oy=self.origin;sx,sy=self.world_scale
  return {k:((x-ox)*sx,(y-oy)*sy,w*sx,h*sy) for k,(x,y,w,h) in rects.items()}
 def sync(self):
  if self.closed:return False
  try:
   clients=self.h.request('clients',True)
   matched={role:next((c for c in clients if c.get('initialTitle')==self.title+'-'+role),None) for role in self.windows}
   for role,c in matched.items():
    if c is None:
     if role not in self.pending:self.close();return False
     continue
    if role in self.pending:
     x,y,w,h=self.monitor if role=='air' else self.starts[role];sel=json.dumps('address:'+c['address'])
     self.h.run(f'hl.dsp.window.resize({{window={sel},x={w},y={h}}})',f'hl.dsp.window.move({{window={sel},x={x},y={y}}})')
     self.pending.remove(role)
     if role.startswith('attack'):
      difficulty=settings(self.game.playtime);health=difficulty['node_hp']
      self.game.nodes[role]={'hp':health,'max':health,'cool':self.game.rng.uniform(difficulty['reinforce_low'],difficulty['reinforce_high'])}
      bx,by,bw,bh=self.board.rects[role];index=int(role[6:])
      for i in range(min(difficulty['ships'],max(0,difficulty['cap']-len(self.game.enemies)))):
       e=Enemy(bx+bw*(.4+i*.12),by+bh*.5,0 if self.game.playtime<25 else index%3,2 if self.game.playtime>=25 and index%3==2 else 1,cool=4+i);e.room=role;self.game.enemies.append(e)
     if role=='home':self.h.focus(c['address']);self.placed=True;print(f'READY workspace={self.workspace}: install, then defend against popup invaders.',flush=True)
     return True
   if any(c is None for c in matched.values()):return True
   rects={r:tuple(c['at']+c['size']) for r,c in matched.items() if c and r!='air'}
   if rects:self.board.relocate(self.world_rects(rects),self.game);self.rects=rects
   self.visible=self.h.request('activeworkspace',True)['id']==self.workspace
   if self.visible:
    cursor=self.h.request('cursorpos',True);ox,oy=self.origin;sx,sy=self.world_scale;self.aim=((cursor['x']-ox)*sx,(cursor['y']-oy)*sy)
   else:self.keys.clear();self.shooting=False
   return True
  except Exception as e:print(f'Room sync: {e}',flush=True);self.close();return False
 def unfocus(self,*_):
  # Focus can move to the transparent desktop surface after its button press.
  # Wait for the compositor's new target before deciding to cancel input.
  GLib.timeout_add(50,self.check_input_focus)
  return False
 def check_input_focus(self):
  if self.closed:return False
  try:
   active=self.h.request('activewindow',True)
   self.update_input_focus(active.get('initialTitle',''))
  except Exception:
   self.keys.clear();self.shooting=False
  return False
 def update_input_focus(self,title):
  if not title.startswith(self.title+'-'):
   self.keys.clear();self.shooting=False
 def draw_room(self,area,c,role):
  if role!='air' and role not in self.board.rects:return
  width,height=area.get_allocated_width(),area.get_allocated_height()
  if role=='air':
   c.set_operator(cairo.OPERATOR_CLEAR);c.paint();c.set_operator(cairo.OPERATOR_OVER)
   if self.game.state not in ('play','over','secured'):return
   c.scale(width/W,height/H)
   for p in self.game.pickups:pickup_art(c,p,min(4,self.game.lasers+1))
   for enemy in self.game.enemies:enemy_art(c,enemy)
   for b in self.game.shots:
    angle=math.atan2(b.vy,b.vx);c.move_to(b.x-math.cos(angle)*14,b.y-math.sin(angle)*14);c.line_to(b.x,b.y);glow(c,'red' if b.enemy else 'cyan',2)
   for p in self.game.sparks:
    c.set_source_rgba(*rgb(p.color),max(0,p.life/p.total));c.arc(p.x,p.y,2,0,math.tau);c.fill()
   return
  if role.startswith('attack'):
   self.draw_attack(area,c,role,width,height);return
  if role=='home' and self.game.state not in ('play','over','secured'):
   c.save();draw(c,self.game,width,height,self.best,self.paused);c.restore()
  else:
   x,y,w,h=self.board.rects[role];view=copy.copy(self.game);view.enemies=list(self.game.enemies)
   c.save();c.scale(width/w,height/h);c.translate(-x,-y);draw(c,view,W,H,self.best,False,sector=True,show_ship=role=='home');c.restore()
   if role.startswith('attack'):
    # Tilt the intrusion graphics, while keeping hit positions honest.
    c.save();c.translate(width/2,height/2);c.rotate(self.tilts[role]);c.set_source_rgba(*rgb('red'),.18);c.set_line_width(2)
    c.rectangle(-width*.42,-height*.35,width*.84,height*.7);c.stroke()
    text(c,'UNAUTHORIZED ACCESS',-width*.35,-height*.23,13,'red');c.restore()
    count=len(view.enemies);text(c,f'{count} INTRUDERS / SHOOT TO CLOSE',12,height-12,11,'orange')
    age=self.visual_age.get(role,1)
    if age<.22:
     c.set_source_rgba(*rgb('red'),(.22-age)*1.7);c.paint()
   else:
    text(c,f'{self.game.score:06} / SHIELDS {self.game.hp} / LASERS {self.game.lasers}/4',12,height-12,12)
    if self.game.upgrade_flash>0:
     text(c,('DUAL','TRIPLE','QUAD')[self.game.lasers-2]+' LASERS ONLINE',width/2,48,15,'bright_green',True)
    if self.game.state=='over':text(c,'BREACHED / R TO REBOOT',width/2-135,height/2,18,'red')
    elif self.game.state=='secured':text(c,'SYSTEM SECURED / R TO REPLAY',width/2-180,height/2,20,'bright_green')
    elif self.paused:text(c,'PAUSED / P TO RESUME',width/2-130,height/2,18,'yellow')
  c.set_source_rgba(*rgb('dark_background'),.95);c.rectangle(0,0,width,27);c.fill()
  title='OMARCHY INSTALLER' if role=='home' else 'INTRUSION // '+role[6:].zfill(2)
  text(c,title,10,18,11,'cyan' if role=='home' else 'red')
  c.set_source_rgb(*rgb('cyan' if role=='home' else 'red'));c.set_line_width(2);c.rectangle(1,1,width-2,height-2);c.stroke()
 def draw_attack(self,area,c,role,width,height):
  c.set_operator(cairo.OPERATOR_CLEAR);c.paint();c.set_operator(cairo.OPERATOR_OVER)
  angle=self.tilts[role];fw,fh=width*.78,height*.65
  c.save();c.translate(width/2,height/2);c.rotate(angle);c.rectangle(-fw/2,-fh/2,fw,fh);c.restore()
  c.save();c.clip()
  x,y,w,h=self.board.rects[role];view=copy.copy(self.game);view.enemies=list(self.game.enemies)
  c.save();c.scale(width/w,height/h);c.translate(-x,-y);draw(c,view,W,H,self.best,False,sector=True,show_ship=False);c.restore()
  age=self.visual_age.get(role,1)
  if age<.22:c.set_source_rgba(*rgb('red'),(.22-age)*1.7);c.paint()
  c.restore()
  c.save();c.translate(width/2,height/2);c.rotate(angle)
  c.set_source_rgb(*rgb('dark_background'));c.rectangle(-fw/2,-fh/2,fw,24);c.fill()
  factions=[('BLOAT PATROL','TOO MANY PACKAGES','orange'),('ARCH GATEKEEPER','INSTALL IT YOURSELF','cyan'),('DOTFILE TRIBUNAL','JUST DOTFILES','blue'),('DEFAULT POLICE','WHO PICKED THIS THEME?','yellow'),('NIX PURIST',"WHERE'S YOUR FLAKE?",'cyan'),('DISCOURSE STORM','ANOTHER 200-REPLY THREAD','red')]
  name,complaint,color=factions[int(role[6:])%len(factions)]
  text(c,'INCOMING / '+role[6:].zfill(2),-fw/2+9,-fh/2+16,10,color)
  c.save();c.rectangle(-fw/2+5,-fh/2+25,fw-10,fh-62);c.clip()
  # Large identity banner remains legible on the smaller popup windows.
  c.set_source_rgba(*rgb(color),.10);c.rectangle(-fw/2+5,-fh/2+25,fw-10,min(78,fh*.48));c.fill()
  words=name.split()
  title_size=min(26,(fw-28)/(max(map(len,words))*.67),fh*.13)
  for i,word in enumerate(words):
   text(c,word,0,-fh/2+30+title_size*(i+1),title_size,color,True)
  text(c,complaint,0,fh/2-46,min(12,(fw-24)/(len(complaint)*.65)),color,True)
  # A tiny animated argument meter and scanning underline.
  for i in range(12):
   bar=3+10*math.sin(self.game.clock*3+i*.8)**2
   c.set_source_rgba(*rgb(color),.3);c.rectangle(fw/2-96+i*7,fh/2-27-bar,4,bar);c.fill()
  c.restore()
  node=self.game.nodes.get(role,{'hp':14,'max':14});ratio=max(0,node['hp']/node['max'])
  c.set_source_rgb(*rgb('background'));c.rectangle(-fw/2+9,fh/2-21,fw-18,7);c.fill()
  c.set_source_rgb(*rgb('red' if ratio<.3 else 'orange'));c.rectangle(-fw/2+9,fh/2-21,(fw-18)*ratio,7);c.fill()
  text(c,f'NODE {node["hp"]}/{node["max"]}',-fw/2+9,fh/2-27,10,'orange')
  c.set_source_rgba(*rgb(color),.17+.12*math.sin(self.game.clock*3)**2);c.set_line_width(6);c.rectangle(-fw/2,-fh/2,fw,fh);c.stroke()
  c.set_source_rgb(*rgb(color));c.set_line_width(1.5);c.rectangle(-fw/2,-fh/2,fw,fh);c.stroke();c.restore()
 def key(self,w,e):
  k=Gdk.keyval_name(e.keyval).lower();fresh=k not in self.keys;self.keys.add(k)
  if k=='escape':self.close()
  elif k=='p' and fresh and self.game.state=='play':self.paused=not self.paused
  elif k=='r' and fresh:
   self.reset()
  elif k in ('space','return') and self.game.state=='title':self.game.state='install';self.game.age=0.
  return True
 def release(self,w,e):self.keys.discard(Gdk.keyval_name(e.keyval).lower());return True
 def motion(self,w,e,role):
  if role=='air':
   self.aim=(e.x*W/w.get_allocated_width(),e.y*H/w.get_allocated_height());return True
  if role not in self.board.rects:return True
  x,y,ww,hh=self.board.rects[role];self.aim=(x+e.x*ww/w.get_allocated_width(),y+e.y*hh/w.get_allocated_height());return True
 def button(self,w,e,role):
  self.motion(w,e,role)
  if e.button==1:
   pressed=e.type==Gdk.EventType.BUTTON_PRESS
   if pressed and role=='home' and e.y<27:
    self.windows[role].begin_move_drag(1,int(e.x_root),int(e.y_root),e.time);return True
   self.shooting=pressed
   if pressed and self.game.state=='title':self.game.state='install';self.game.age=0.
  return True
 def save(self):
  if self.game.score<=self.best:return
  self.best=self.game.score
  try:
   self.bestpath.parent.mkdir(parents=True,exist_ok=True);tmp=self.bestpath.with_suffix(f'.{os.getpid()}.tmp');tmp.write_text(json.dumps({'best':self.best}));tmp.replace(self.bestpath)
  except OSError as e:print(f'Could not save best score: {e}',flush=True)
 def tick(self):
  if self.closed:return False
  now=time.monotonic();dt=min(.04,now-self.last);self.last=now
  if not self.paused and self.placed and self.visible:
   k=self.keys;move=(int('d' in k or 'right' in k)-int('a' in k or 'left' in k),int('s' in k or 'down' in k)-int('w' in k or 'up' in k))
   self.game.step(dt,move,self.aim,self.shooting,'space' in k)
   if self.game.state=='play':
    self.attack_clock+=dt
    for role in self.visual_age:self.visual_age[role]+=dt
    due=settings(self.game.playtime)['rooms']
    while len(self.spawned_rooms)<due:self.open_attack(f'attack{len(self.spawned_rooms)}')
    for role,node in list(self.game.nodes.items()):
     if node['hp']<=0 and role in self.windows:
      self.cleared.add(role);self.windows.pop(role).destroy();self.areas.pop(role);self.rects.pop(role,None);self.board.rects.pop(role,None);self.game.nodes.pop(role)
    active={role for role in self.windows if role.startswith('attack')}
    for role in replacements(active,self.game.respawns,self.game.playtime):
     self.game.respawns.pop(role);self.randomize_attack(role);self.open_attack(role)
   if self.game.state=='over':self.save()
  if self.visible:
   for area in self.areas.values():area.queue_draw()
  return True
 def close(self):
  if self.closed:return False
  self.closed=True;self.save()
  for win in self.windows.values():win.destroy()
  try:
   self.h.request(f'eval {self.rule}:set_enabled(false); {self.rule}=nil; {self.rule}_air:set_enabled(false); {self.rule}_air=nil; {self.rule}_attacks:set_enabled(false); {self.rule}_attacks=nil')
   if self.h.request('activeworkspace',True)['id']==self.workspace:self.h.run(f'hl.dsp.focus({{workspace={json.dumps(self.previous)}}})')
  except Exception:pass
  if Gtk.main_level():Gtk.main_quit()
  return False

if __name__=='__main__':
 app=App()
 try:Gtk.main()
 finally:app.close()

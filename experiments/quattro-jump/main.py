#!/usr/bin/env python3
"""Three floating windows, one sunset rally jump. Hold Space, release to launch."""
import json,math,os,signal,sys,time,random
from functools import lru_cache
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from hyprsplitter import Hyprland
from experiments.rally import quattro
from experiments.theme import PALETTE
from model import Jump,ramp_y,sun_target,landing_target,landing_y,landing_slope
import gi
for name,version in [('Gtk','3.0'),('Gdk','3.0'),('GLibUnix','2.0')]:gi.require_version(name,version)
from gi.repository import Gtk,Gdk,GLib,GLibUnix
import cairo

PINK=(1,.10,.49);GOLD=(1,.76,.34);PURPLE=(.20,.05,.30);INK=(.075,.035,.14)
# Local process palette: the existing car takes on the reference's sunset light.
PALETTE.update(foreground=(1,.82,.70),red=(.96,.15,.43),orange=(1,.43,.24),blue=(.39,.24,.64),bright_yellow=(1,.90,.49),dark_background=INK,muted=(.33,.16,.40),yellow=GOLD)

def text(c,s,x,y,size=13,color=(1,.83,.81)):
 c.set_source_rgb(*color);c.select_font_face('monospace',0,0);c.set_font_size(size);c.move_to(x,y);c.show_text(s)
def path(c,points,color):
 c.set_source_rgb(*color);c.move_to(*points[0])
 for p in points[1:]:c.line_to(*p)
 c.close_path();c.fill()

def rally_sign(c,w,h,t,landed=False,age=0):
 # A landing gust dies away into the normal breeze.
 gust=math.exp(-age*1.4)*math.sin(age*13) if landed else 0
 width=min(130,w*.34);left=w-width-24;top=landing_y(w,h,left)-106
 for x in (left-5,left+width+5):
  c.set_source_rgb(.13,.055,.18);c.set_line_width(3)
  c.move_to(x,top-6);c.line_to(x-5,landing_y(w,h,x));c.stroke()
 c.save();c.translate(left,top);c.scale(width/205,width/205);width=205
 c.transform(cairo.Matrix(1,gust*.025,gust*.13,1,0,0))
 for x in range(int(width)):
  wave=math.sin(x*.045-t*3.8)*(3.5+abs(gust)*10)+math.sin(x*.02-t*2)*2+x*.045
  c.set_source_rgb(.075,.025,.12);c.rectangle(x,wave,2.2,87);c.fill()
 c.transform(cairo.Matrix(1,.045,0,1,0,0))
 c.set_source_rgb(.77,.20,.55);c.select_font_face('sans-serif',cairo.FONT_SLANT_ITALIC,cairo.FONT_WEIGHT_BOLD)
 c.set_font_size(width/7);c.move_to(9,35);c.show_text('quattro')
 for i in range(4):
  c.set_source_rgba(*PINK,.55);c.rectangle(12,49+i*5,width*.48,2);c.fill()
 for i in range(4):
  c.set_source_rgba(.95,.43,.71,.85);c.set_line_width(2)
  c.arc(width*.66+i*width*.075,62,width*.053,0,math.tau);c.stroke()
 if landed:
  glint=(t*.45)%1;c.set_source_rgba(*GOLD,.16)
  c.rectangle(glint*(width+30)-30,4,12,80);c.fill()
 c.restore()

def spectators(c,w,h,t,landed,age):
 for i,u in enumerate((.12,.25,.38)):
  x=w*u;y=landing_y(w,h,x)-5;bob=math.sin(t*1.5+i)*.6
  c.set_source_rgb(.10,.035,.17);c.set_line_width(3);c.set_line_cap(cairo.LINE_CAP_ROUND)
  c.move_to(x-4,y);c.line_to(x-2,y-12);c.line_to(x+3,y-12);c.line_to(x+6,y);c.stroke()
  c.move_to(x,y-12);c.line_to(x,y-24+bob);c.stroke()
  c.arc(x,y-30+bob,4,0,math.tau);c.fill()
  c.move_to(x,y-21+bob);c.line_to(x+7,y-25+bob);c.line_to(x+10,y-24+bob);c.stroke()
  c.rectangle(x+6,y-28+bob,8,5);c.fill()
  # Each camera fires twice, in a short staggered sequence after touchdown.
  strength=0
  if landed:
   for delay in (.07+i*.17,.83+i*.12):strength=max(strength,max(0,1-abs(age-delay)/.085))
  if strength>0:
   fx,fy=x+13,y-27+bob
   glow=cairo.RadialGradient(fx,fy,0,fx,fy,24)
   glow.add_color_stop_rgba(0,1,.96,.85,strength*.9);glow.add_color_stop_rgba(1,1,.8,.6,0)
   c.set_source(glow);c.arc(fx,fy,24,0,math.tau);c.fill()
   c.set_source_rgba(1,1,.95,strength);c.set_line_width(1.5)
   for angle in (0,math.pi/2,math.pi/4,-math.pi/4):
    dx,dy=math.cos(angle)*9,math.sin(angle)*9
    c.move_to(fx-dx,fy-dy);c.line_to(fx+dx,fy+dy);c.stroke()

def atmosphere(c,w,h,t,role):
 # Dust motes catch the sunset at different depths.
 for i in range(28):
  depth=.3+(i%5)*.16;x=(i*71.7+t*(9+depth*16))%(w+30)-15
  y=h*.30+(i*43.3)%(h*.58)+math.sin(t*.7+i)*8
  alpha=(.12+.15*math.sin(t*1.2+i)**2)*depth
  c.set_source_rgba(*GOLD,alpha);c.arc(x,y,.7+depth,0,math.tau);c.fill()
 # A small flock traces lazy arcs through the sun window.
 if role=='sky':
  for i in range(5):
   x=(t*17+i*17)%(w+100)-50;y=h*.23+math.sin(t*.5+i*.3)*13+i*3
   flap=math.sin(t*7-i)*3
   c.set_source_rgba(*INK,.55);c.set_line_width(1.3)
   c.move_to(x-4,y-flap);c.line_to(x,y);c.line_to(x+4,y-flap);c.stroke()

@lru_cache(maxsize=24)
def scrub_layout(w,role):
 rng=random.Random(71 if role=='ramp' else 193)
 clusters=[]
 for _ in range(max(3,int(w/65))):
  center=rng.uniform(5,w-5)
  for _ in range(rng.randint(3,8)):
   clusters.append((center+rng.uniform(-14,14),rng.uniform(3,15),rng.uniform(-7,7),rng.random()*math.tau,rng.uniform(.35,.85)))
 rocks=[(rng.uniform(0,w),rng.uniform(1,4),rng.uniform(1,2.5)) for _ in range(int(w/28))]
 return clusters,rocks

def roadside(c,w,h,t,role,rise=90):
 surface=(lambda w,h,x:ramp_y(w,h,x,rise)) if role=='ramp' else landing_y
 clusters,rocks=scrub_layout(w,role)
 for x,length,bend,phase,alpha in clusters:
  y=surface(w,h,x);gust=math.sin(t*1.7+phase)*length*.15
  c.set_source_rgba(.59,.15,.36,alpha);c.set_line_width(.8+length*.035)
  c.move_to(x,y);c.curve_to(x+bend*.3,y-length*.4,x+bend+gust,y-length*.8,x+bend+gust,y-length);c.stroke()
  if length>10:
   c.move_to(x+bend*.4,y-length*.5);c.line_to(x+bend+3,y-length*.75);c.stroke()
 for x,rise,width in rocks:
  y=surface(w,h,x)
  path(c,[(x-width,y),(x-width*.6,y-rise),(x+width*.4,y-rise*.7),(x+width,y)],(.27,.09,.24))
 for i in range(7):
  x=(t*(35+i*3)+i*79)%(w+80)-40;y=surface(w,h,x)-7-i%3*4
  c.set_source_rgba(*PINK,.10);c.set_line_width(1.4)
  c.move_to(x-18,y+2);c.curve_to(x-6,y-3,x+9,y-3,x+24,y);c.stroke()

def launch_dust(c,w,h,age,rise=90):
 if not 0<age<1.65:return
 x=w*.88;y=ramp_y(w,h,x,rise)
 # Backlit billowing dust, anchored to the lip rather than following the car.
 for i in range(32):
  delay=(i%5)*.022;life=age-delay
  if life<=0:continue
  fade=max(0,1-life/1.65)
  speed=28+(i*37)%95
  px=x-12-life*speed;py=y-5-life*(22+(i*23)%100)+life*life*22
  radius=(7+(i*11)%16)*(1+life*.9)
  glow=cairo.RadialGradient(px,py,0,px,py,radius)
  color=GOLD if i%4==0 else (1,.26,.39) if i%3 else PINK
  glow.add_color_stop_rgba(0,*color,fade*.38);glow.add_color_stop_rgba(1,*color,0)
  c.set_source(glow);c.arc(px,py,radius,0,math.tau);c.fill()
 for i in range(38):
  speed=30+(i*19)%130;angle=2.5+(i%13)*.13
  px=x+math.cos(angle)*speed*age;py=y-math.sin(angle)*speed*age+95*age*age
  c.set_source_rgba(*(GOLD if i%4==0 else (.35,.08,.22)),max(0,1-age/1.4))
  c.rectangle(px,py,1+i%3,1+i%2);c.fill()

def tire_dust(c,x,y,t,strength,age=None):
 for i in range(18):
  life=(t*1.5+i*.137)%1 if age is None else age+i*.008
  if life>1:continue
  dx=-15-life*(30+i%4*8);dy=-life*(6+i%5*3)
  c.set_source_rgba(*(GOLD if i%3==0 else PINK),strength*(1-life)*.22)
  c.arc(x+dx,y+dy,2+life*6,0,math.tau);c.fill()

def fireworks(c,w,h,age):
 for burst in range(5):
  elapsed=age-burst*.3
  if not 0<=elapsed<=1.6:continue
  cx=w*(.24+(burst%3)*.25);cy=h*(.24+(burst%2)*.18)
  fade=max(0,1-elapsed/1.6)
  for i in range(32):
   angle=i*math.tau/32+burst*.5;speed=42+(i%3)*22
   radius=speed*elapsed
   x=cx+math.cos(angle)*radius;y=cy+math.sin(angle)*radius+25*elapsed*elapsed
   c.set_source_rgba(*(GOLD if i%3 else PINK),fade);c.set_line_width(1.8)
   c.move_to(x-math.cos(angle)*7*fade,y-math.sin(angle)*7*fade);c.line_to(x,y);c.stroke()
   c.arc(x,y,1.7*fade,0,math.tau);c.fill()

class Demo:
 def __init__(self):
  self.hypr=Hyprland();self.prefix=f'QuattroJump-{os.getpid()}';self.rule=f'quattro_jump_{os.getpid()}'
  self.closed=False;self.ready=False;self.windows={};self.clients={};self.g={};self.game=Jump();self.last=time.monotonic();self.start=self.last;self.visible=False
  self.previous=self.hypr.request('activeworkspace',True)['name'];used={w['id'] for w in self.hypr.request('workspaces',True)}
  self.workspace=next(i for i in range(2,1000) if i not in used)
  m=next(m for m in self.hypr.request('monitors',True) if m['focused']);mw=m['width']/m['scale'];mh=m['height']/m['scale']
  scale=min(1,(mw-80)/1360);rw=int(420*scale);sw=int(520*scale);base=int(m['y']+mh*.48);left=int(m['x']+(mw-1360*scale)/2)
  self.initial={'ramp':(left,base,rw,360),'sky':(left+rw,base-65,sw,450),'landing':(left+rw+sw,base,rw,360)}
  self.hypr.request(f'eval {self.rule}=hl.window_rule({{name="{self.rule}",match={{initial_title="^{self.prefix}-.*$"}},workspace="{self.workspace}",float=true,no_anim=true,rounding=0,opacity="1 override 1 override"}})')
  self.hypr.run(f'hl.dsp.focus({{workspace="{self.workspace}"}})')
  for role,rect in self.initial.items():
   win=Gtk.Window(title=f'{self.prefix}-{role}');win.set_decorated(False);win.set_default_size(*rect[2:])
   win.connect('delete-event',lambda *_:self.close());win.connect('key-press-event',self.key,True);win.connect('key-release-event',self.key,False)
   area=Gtk.DrawingArea();area.add_events(Gdk.EventMask.BUTTON_PRESS_MASK);area.connect('button-press-event',self.drag,win,role);area.connect('draw',self.draw,role)
   win.add(area);win.show_all();self.windows[role]=win
  GLib.timeout_add(50,self.sync);GLib.timeout_add(16,self.tick)
  for sig in (signal.SIGTERM,signal.SIGINT):GLibUnix.signal_add(GLib.PRIORITY_DEFAULT,sig,self.close)
 def reset(self):
  self.game=Jump(self.game.rise)
 def adjust_ramp(self,direction):
  if self.game.state not in ('ready','charging'):return
  width=self.g.get('ramp',self.initial['ramp'])[2]
  angle=math.degrees(math.atan2(self.game.rise,width*.5))
  self.game.rise=math.tan(math.radians(max(8,min(38,angle+direction*2))))*width*.5
 def drag(self,a,e,w,role):
  if role=='ramp' and e.button==1 and 35<=e.y<=65 and 12<=e.x<=180:
   self.adjust_ramp(-1 if e.x<95 else 1);return True
  if e.button==1:w.begin_move_drag(1,int(e.x_root),int(e.y_root),e.time)
  return True
 def key(self,w,e,pressed):
  k=Gdk.keyval_name(e.keyval).lower()
  if k=='space':
   if pressed and self.game.state in ('landed','missed'):
    self.reset()
   if pressed and self.game.state=='ready':self.game.state='charging'
   elif not pressed:self.game.release()
  elif pressed and k in ('up','down'):self.adjust_ramp(1 if k=='up' else -1)
  elif pressed and k=='r':self.reset()
  elif pressed and k=='escape':self.close()
  return True
 def sync(self):
  if self.closed:return False
  try:
   clients=self.hypr.request('clients',True)
   self.clients={r:next((c for c in clients if c.get('initialTitle')==f'{self.prefix}-{r}'),None) for r in self.windows}
   if not all(self.clients.values()):
    if self.ready or time.monotonic()-self.start>10:self.close();return False
    return True
   if not self.ready:
    for r,c in self.clients.items():
     x,y,w,h=self.initial[r];sel=json.dumps('address:'+c['address'])
     self.hypr.run(f'hl.dsp.window.resize({{window={sel},x={w},y={h}}})',f'hl.dsp.window.move({{window={sel},x={x},y={y}}})')
    self.ready=True;self.hypr.focus(self.clients['ramp']['address']);print(f'READY workspace={self.workspace}: hold Space, release to jump. R retry.',flush=True)
   self.g={r:tuple(c['at']+c['size']) for r,c in self.clients.items()}
   self.visible=self.hypr.request('activeworkspace',True)['id']==self.workspace
   if not self.visible and self.game.state=='charging':self.game.state='ready';self.game.charge=0
  except Exception as e:print(e,flush=True);self.close();return False
  return True
 def tick(self):
  if self.closed:return False
  now=time.monotonic();dt=min(.05,now-self.last);self.last=now
  if self.ready and self.g and self.visible:self.game.step(dt,self.g)
  if self.visible:
   for w in self.windows.values():w.queue_draw()
  return True
 def draw(self,a,c,role):
  w,h=a.get_allocated_width(),a.get_allocated_height();t=time.monotonic()-self.start
  grad=cairo.LinearGradient(0,0,0,h);grad.add_color_stop_rgb(0,.24,.055,.39);grad.add_color_stop_rgb(.43,.98,.12,.48);grad.add_color_stop_rgb(1,1,.52,.28);c.set_source(grad);c.paint()
  if role=='sky':
   sunx=w*.56;suny=h*.48;radius=min(w,h)*.27
   halo=cairo.RadialGradient(sunx,suny,radius*.6,sunx,suny,radius*1.65)
   halo.add_color_stop_rgba(0,1,.76,.28,.22+.07*math.sin(t*1.5));halo.add_color_stop_rgba(1,1,.4,.3,0)
   c.set_source(halo);c.paint()
   c.save();c.arc(sunx,suny,radius,0,math.tau);c.clip();c.set_source_rgb(1,.87,.37);c.paint()
   for i in range(7):
    c.set_source_rgba(1,.30,.39,.85);c.rectangle(sunx-radius,suny+15+i*12+math.sin(t*1.2+i*.7)*2,radius*2,2+i*.7);c.fill()
   c.restore()
  # Long illuminated cloud streaks move gently across each window.
  for i in range(12):
   x=((i*103+t*(9+i%3*5))%(w+150))-100;y=48+(i*31)%int(h*.58)+math.sin(t*.8+i)*4
   path(c,[(x,y),(x+75,y-8),(x+120,y-6),(x+44,y+3)],(1,.31+i%3*.05,.48))
  for layer in range(3):
   pts=[(0,h)]+[(x,h-40-layer*25-abs(math.sin(x*.009+layer*2))*45) for x in range(0,w+12,12)]+[(w,h)]
   path(c,pts,(.22-layer*.04,.065,.29-layer*.035))
  atmosphere(c,w,h,t,role)
  if role in ('ramp','landing'):
   points=[(x,ramp_y(w,h,x,self.game.rise) if role=='ramp' else landing_y(w,h,x)) for x in range(0,w+4,3)]
   path(c,[(0,h)]+points+[(w,h)],INK)
   c.set_source_rgb(*PINK);c.set_line_width(3);c.move_to(*points[0])
   for p in points[1:]:c.line_to(*p)
   c.stroke()
   for i in range(int(w/16)):
    x=i*16;y=ramp_y(w,h,x,self.game.rise) if role=='ramp' else landing_y(w,h,x)
    c.set_source_rgba(1,.3,.5,.3);c.rectangle(x,y+10,7,2);c.fill()
   roadside(c,w,h,t,role,self.game.rise)
   if role=='landing':
    if self.game.state=='landed':
     # Tire tracks stay attached to the landing window when it is moved.
     start=getattr(self.game,'touchdown_local',self.game.local);end=self.game.local
     for offset in (-17,18):
      c.set_source_rgba(.035,.015,.065,.85);c.set_line_width(3)
      for step in range(25):
       u=step/24;x=start+(end-start)*u+offset;y=landing_y(w,h,x)+4+math.sin(u*math.pi)*offset*.17
       if step==0:c.move_to(x,y)
       else:c.line_to(x,y)
      c.stroke()
    spectators(c,w,h,t,self.game.state=='landed',self.game.result_age)
    rally_sign(c,w,h,t,self.game.state=='landed',self.game.result_age)
  game=self.game
  if role=='ramp' and game.state in ('flying','landed','missed'):
   launch_dust(c,w,h,game.airtime+game.result_age,game.rise)
  if role=='sky' and game.fireworks:fireworks(c,w,h,game.firework_age)
  if role=='ramp':
   status='release to launch' if game.state=='charging' else 'hold Space to launch  /  R reset'
   text(c,status,18,27,11)
   angle=math.degrees(math.atan2(game.rise,w*.5))
   text(c,f'−  ramp {angle:.0f}°  +   ↑ / ↓',18,54,12)
   if game.state=='charging':
    c.set_source_rgba(*INK,.5);c.rectangle(18,69,w-36,4);c.fill()
    c.set_source_rgb(*GOLD);c.rectangle(18,69,(w-36)*game.charge,4);c.fill()
  if role in self.g and game.state=='missed' and game.result_age<1:
   # Keep impact feedback visible even when the missed car left the windows.
   if role=='landing':
    age=game.result_age;x=max(30,min(w-30,game.x-self.g[role][0]));y=h-48
    for i in range(28):
     angle=i*2.4;speed=35+(i%7)*18
     c.set_source_rgba(*(GOLD if i%2 else PINK),1-age);c.rectangle(x+math.cos(angle)*speed*age,y-abs(math.sin(angle))*speed*age+80*age*age,3,3);c.fill()

  if role in self.g and game.state!='missed':
   ox,oy=self.g[role][:2]
   # A tapered hot core, magenta glow and drifting embers follow the flight.
   for i in range(1,len(game.trail)):
    x0,y0=game.trail[i-1];x1,y1=game.trail[i];strength=i/len(game.trail)
    for color,width,alpha in ((PINK,14,.18),(PINK,7,.55),(GOLD,2.5,.9)):
     c.set_source_rgba(*color,strength*alpha);c.set_line_width(width*strength)
     c.move_to(x0-ox-22,y0-oy);c.line_to(x1-ox-22,y1-oy);c.stroke()
    if i%2==0:
     drift=(1-strength)*18
     c.set_source_rgba(*GOLD,strength*.8);c.rectangle(x0-ox-30,y0-oy+math.sin(i*4+t*8)*drift,2,2);c.fill()
   lean=math.atan2(game.vy,game.vx) if game.state=='flying' else -math.atan2(game.rise,self.g['ramp'][2]*.5) if role=='ramp' and game.local>w*.38 and game.state=='runup' else 0
   if game.state=='landed':
    _,_,lw,lh=self.g['landing'];lean=math.atan(landing_slope(lw,lh,game.local))
   jitter=math.sin(t*75)*game.charge*1.3 if game.state=='charging' else 0
   if game.state in ('ready','charging','runup'):
    tire_dust(c,game.x-ox-16,game.y-oy-3,t,.2+game.charge*.8)
   if game.state=='landed' and game.result_age<1:
    tire_dust(c,game.x-ox-5,game.y-oy,t,1,game.result_age)
   carx=game.x-ox+jitter;cary=game.y-oy-abs(jitter)
   c.save()
   if game.state=='landed' and game.result_age<1.05:
    age=game.result_age;slide=math.sin(min(1,age/.9)*math.pi)*(1-age/1.05)
    c.translate(carx,cary);c.transform(cairo.Matrix(1-slide*.14,0,slide*.48,1,slide*7,0));c.translate(-carx,-cary)
   c.translate(carx,cary);c.scale(.78,.78)
   quattro(c,0,0,t,walking=game.state in ('runup','flying') or (game.state=='landed' and game.vx>2),lean=lean,phase=t*15,happy=False,landing=max(0,1-game.result_age*4) if game.state=='landed' else 0)
   if game.state=='landed':
    brake=min(1,game.vx/40)*.85+max(0,1-game.result_age/1.2)*.15
    if brake>0:
     c.save();c.translate(0,-11);c.rotate(lean)
     glow=cairo.RadialGradient(-43,-12,0,-43,-12,23)
     glow.add_color_stop_rgba(0,1,.08,.12,brake*.85);glow.add_color_stop_rgba(1,1,.04,.1,0)
     c.set_source(glow);c.arc(-43,-12,23,0,math.tau);c.fill()
     c.set_source_rgba(1,.17,.15,brake);c.rectangle(-45,-16,5,7);c.fill()
     c.set_source_rgba(1,.7,.47,brake);c.rectangle(-44,-15,2,4);c.fill();c.restore()
   c.restore()
   if game.state=='landed' and game.result_age<1.1:
    age=game.result_age
    for i in range(12):
     life=age-i*.018
     if life<0:continue
     c.set_source_rgba(.92,.68,.76,max(0,1-life/1.1)*.22)
     c.arc(carx-22-life*(35+i*2),cary-4-life*(12+i%4*6),3+life*13,0,math.tau);c.fill()

  return False
 def close(self):
  if self.closed:return False
  self.closed=True
  for w in self.windows.values():w.destroy()
  try:
   self.hypr.request(f'eval {self.rule}:set_enabled(false); {self.rule}=nil')
   if self.hypr.request('activeworkspace',True)['id']==self.workspace:self.hypr.run(f'hl.dsp.focus({{workspace={json.dumps(self.previous)}}})')
  except Exception:pass
  if Gtk.main_level():Gtk.main_quit()
  return False

if __name__=='__main__':
 app=Demo()
 try:Gtk.main()
 finally:app.close()

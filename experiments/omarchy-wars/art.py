"""Neon wireframes, stepped Omarchy O ship, and a fictional install intro."""
import math,cairo
from experiments.theme import rgb
from model import W,H,WARNING_DURATION,INSTALL_DURATION
from branding import wordmark

def text(c,s,x,y,size=16,col='foreground',center=False):
 c.select_font_face('monospace',0,cairo.FONT_WEIGHT_BOLD);c.set_font_size(size);c.set_source_rgb(*rgb(col))
 if center:x-=c.text_extents(s).width/2
 c.move_to(x,y);c.show_text(s)
def glow(c,col,width=2):
 for size,alpha in ((width+12,.035),(width+6,.09),(width,.95)):
  c.set_source_rgba(*rgb(col),alpha);c.set_line_width(size);c.stroke_preserve()
 c.new_path()
def o_path(c,r=19):
 # Stepped corners and upright hollow center echo the Omarchy wordmark.
 pts=[(-.45,-1),(.45,-1),(.45,-.86),(.72,-.86),(.72,-.64),(.86,-.64),(.86,.64),(.72,.64),(.72,.86),(.45,.86),(.45,1),(-.45,1),(-.45,.86),(-.72,.86),(-.72,.64),(-.86,.64),(-.86,-.64),(-.72,-.64),(-.72,-.86),(-.45,-.86)]
 c.move_to(pts[0][0]*r,pts[0][1]*r)
 for x,y in pts[1:]:c.line_to(x*r,y*r)
 c.close_path()
 c.rectangle(-.36*r,-.64*r,.72*r,1.28*r)
def ship(c,x,y,angle,t,alpha=1):
 c.save();c.translate(x,y);c.rotate(angle)
 for i in range(3):
  length=8+4*math.sin(t*18+i*2)
  c.move_to(-10,-3+i*3);c.line_to(-10-length,-3+i*3);glow(c,'cyan',.7)
 c.restore()
 c.save();c.translate(x,y);c.scale(.52,.52);c.set_fill_rule(cairo.FILL_RULE_EVEN_ODD);o_path(c)
 gradient=cairo.LinearGradient(0,-19,0,19)
 for pos,col in ((0,(.75,.78,.96)),(.25,(.75,.78,.96)),(.26,(.47,.80,.96)),(.82,(.47,.80,.96)),(.83,(.5,.6,.93)),(1,(.5,.6,.93))):gradient.add_color_stop_rgba(pos,*col,alpha)
 c.set_source(gradient);c.fill_preserve();glow(c,'blue',1)
 c.rotate(angle);c.move_to(33,0);c.line_to(24,-3);c.line_to(24,3);c.close_path();c.set_source_rgba(*rgb('cyan'),alpha);c.fill();c.restore()
def digital_skeleton(c,e):
 c.save();c.translate(e.x,e.y)
 # Green fragments stream past an unfilled wire skeleton.
 c.select_font_face('monospace',0,0);c.set_font_size(5)
 for i in range(5):
  phase=(e.age*.8+i*.21)%1
  c.set_source_rgba(.12,1,.35,(1-phase)*.55)
  c.move_to(-12+i*5,-15+phase*30);c.show_text('1' if (int(e.age*5)+i)%2 else '0')
 c.rotate(e.age*(1 if e.kind!=2 else -2));c.scale(.52,.52)
 points=[(0,-17),(17,0),(0,17),(-17,0)] if e.kind==0 else [(-13,-13),(13,-13),(13,13),(-13,13)] if e.kind==1 else [(math.cos(i*math.tau/3)*19,math.sin(i*math.tau/3)*19) for i in range(3)]
 c.move_to(*points[0])
 for point in points[1:]:c.line_to(*point)
 c.close_path();c.set_source_rgba(.15,1,.4,.85);c.set_line_width(1.2);c.stroke()
 c.set_source_rgba(.1,.8,.3,.6);c.set_line_width(.8)
 for x,y in points:c.move_to(0,0);c.line_to(x,y)
 c.stroke()
 for i,(x,y) in enumerate(points):
  c.set_source_rgba(.45,1,.65,.6+.4*math.sin(e.age*8+i)**2);c.rectangle(x-1.5,y-1.5,3,3);c.fill()
 c.restore()

def enemy_art(c,e):
 if getattr(e,'phasing',False):digital_skeleton(c,e);return
 c.save();c.translate(e.x,e.y);c.scale(.52,.52);c.rotate(e.age*(1 if e.kind!=2 else -2))
 if e.age<.65:
  c.arc(0,0,28*(1-e.age/.65)+15,0,math.tau);glow(c,'red',1)
 elif e.kind==0:
  c.move_to(0,-17);c.line_to(17,0);c.line_to(0,17);c.line_to(-17,0);c.close_path();glow(c,'red')
 elif e.kind==1:
  c.rectangle(-13,-13,26,26);c.move_to(-9,0);c.line_to(9,0);c.move_to(0,-9);c.line_to(0,9);glow(c,'orange')
 else:
  for i in range(3):
   a=i*math.tau/3;c.line_to(math.cos(a)*19,math.sin(a)*19) if i else c.move_to(math.cos(a)*19,math.sin(a)*19)
  c.close_path();glow(c,'blue')
 c.restore()

def pickup_art(c,p,level):
 c.save();c.translate(p.x,p.y)
 c.arc(0,0,14+2*math.sin(p.age*4),0,math.tau);glow(c,'bright_green',1)
 for i in range(level):
  x=(i-(level-1)/2)*5
  c.move_to(x,6);c.line_to(x,-6);glow(c,'cyan',1.5)
 a=p.age*2;c.arc(math.cos(a)*19,math.sin(a)*19,2,0,math.tau);c.set_source_rgb(*rgb('yellow'));c.fill()
 c.restore()

def draw(c,g,width,height,best,paused=False,sector=False,show_ship=True):
 c.set_source_rgb(.025,.035,.045);c.paint();s=min(width/W,height/H);c.translate((width-W*s)/2,(height-H*s)/2);c.scale(s,s)
 c.save();c.rectangle(0,0,W,H);c.clip()
 t=g.clock;c.translate(math.sin(t*97)*g.shake,math.cos(t*83)*g.shake)
 c.set_line_width(.7);c.set_source_rgba(*rgb('cyan'),.085)
 for x in range(0,W+1,40):c.move_to(x,76);c.line_to(x,H-34)
 for y in range(76,H-30,40):c.move_to(0,y);c.line_to(W,y)
 c.stroke();c.rectangle(14,77,W-28,H-112);glow(c,'cyan',1)
 if g.state in ('play','over'):
  for p in g.pickups:pickup_art(c,p,min(4,g.lasers+1))
  for e in g.enemies:enemy_art(c,e)
  for b in g.shots:
   a=math.atan2(b.vy,b.vx);c.move_to(b.x-math.cos(a)*14,b.y-math.sin(a)*14);c.line_to(b.x,b.y);glow(c,'orange' if b.enemy else 'cyan',2)
  if g.state=='play' and show_ship:ship(c,g.x,g.y,g.angle,t,.4 if g.invuln and int(t*15)%2 else 1)
 for p in g.sparks:
  c.set_source_rgba(*rgb(p.color),max(0,p.life/p.total));c.set_line_width(2);c.move_to(p.x,p.y);c.line_to(p.x-p.vx*.025,p.y-p.vy*.025);c.stroke()
 c.restore()
 if sector:return
 text(c,'OMARCHY / ZERO DAY',26,38,20,'bright_green');text(c,f'{g.score:07}',W/2,41,28,center=True)
 text(c,f'BEST {best:07}',W-225,36,16,'yellow')
 if g.state in ('play','over'):
  text(c,f'WAVE {g.wave:02}',26,63,12,'cyan');text(c,'SHIELDS '+'O '*max(0,g.hp),W-225,61,12,'bright_green')
  text(c,'WASD MOVE / MOUSE AIM + FIRE / SPACE DASH / P PAUSE',26,H-12,12,'cyan')
  text(c,'DASH READY' if g.dash_cool<=0 else 'RECHARGING',W-160,H-12,12,'yellow')
 else:
  c.set_source_rgba(.025,.035,.045,.88);c.rectangle(150,170,800,385);c.fill()
  if g.state=='title':
   wordmark(c,115,185,870,190)
   text(c,'A fresh install. A new record.',W/2,429,19,'cyan',True)
   c.set_source_rgb(*rgb('bright_green'));c.rectangle(W/2-165,482,330,36);c.fill()
   text(c,'SPACE / INSTALL NOW',W/2,507,19,'dark_background',True)
   text(c,'OMATARI / FICTIONAL INSTALL SEQUENCE',W/2,H-18,11,'muted',True)
  elif g.state=='install':
   progress=min(1,g.age/INSTALL_DURATION);text(c,'INSTALLING OMARCHY',W/2,253,30,'bright_green',True)
   lines=['Partitioning the void','Unpacking a better desktop','Loading community plugins','Starting Hyprland','Welcome home']
   for i,line in enumerate(lines):
    if progress>=i/5:text(c,'[ OK ] '+line,270,300+i*30,16,'cyan')
   c.set_source_rgb(*rgb('background'));c.rectangle(270,476,560,10);c.fill();c.set_source_rgb(*rgb('bright_green'));c.rectangle(270,476,560*progress,10);c.fill()
  elif g.state=='record':
   wordmark(c,115,180,870,185)
   text(c,f'Installed in {INSTALL_DURATION:.2f}s / NEW RECORD',W/2,419,23,'cyan',True)
   text(c,'Remember to remove USB installer!',W/2,458,17,center=True)
   c.set_source_rgb(*rgb('bright_green'));c.rectangle(W/2-110,490,220,30);c.fill()
   text(c,'Reboot Now',W/2,512,18,'dark_background',True)
  else:
   u=min(1,g.age/WARNING_DURATION);ship(c,165+(W/2-165)*u,265+(H/2-265)*u,0,t)
   pulse=.08+.05*math.sin(g.age*4)
   c.set_source_rgba(*rgb('red'),pulse);c.rectangle(150,170,800,385);c.fill()
   scan=180+(g.age*85)%360
   c.set_source_rgba(*rgb('red'),.2);c.rectangle(150,scan,800,2);c.fill()
   for i in range(12):
    x=160+i*65;c.set_source_rgba(*rgb('yellow'),.25+.2*math.sin(g.age*4+i)**2);c.rectangle(x,185,36,4);c.fill()
   text(c,f'DEFENSE ONLINE IN {max(1,math.ceil(WARNING_DURATION-g.age))}',W/2,530,14,'yellow',True)
   text(c,'WARNING!  WARNING!' ,W/2,295,44,'red' if int(g.age*2)%2 else 'yellow',True)
   text(c,'HACKERS ARE ATTEMPTING',W/2,367,26,'red',True)
   text(c,'TO INFILTRATE YOUR SYSTEM',W/2,410,26,'red',True)
   text(c,'DEFEND YOUR INSTALL / AIM + FIRE',W/2,477,18,'cyan',True)
 if g.state=='over' or paused:
  c.set_source_rgba(.025,.035,.045,.85);c.rectangle(210,240,680,255);c.fill()
  text(c,'PAUSED' if paused else 'SESSION BREACHED',W/2,315,36,'yellow' if paused else 'red',True)
  text(c,'P / RESUME' if paused else f'{g.score:,} POINTS / {g.playtime:.1f}s SURVIVED',W/2,375,22,center=True)
  text(c,'ESC / RETURN TO OMATARI' if paused else 'R / REBOOT + RETRY    ESC / EXIT',W/2,442,17,'cyan',True)

import math
import cairo
from style import rgb,text,panel,heading,hint
from hazard_art import minigun,MUZZLE_X,BEAM_HALF_HEIGHT

def lemur(c,x,y,t,fall=False,seed=0,direction=1,slide=False,ride=False,tilt=0.):
 # Keep the shared actor interface so every window draws the same Tux sprite.
 c.save();c.translate(x,y);c.scale(direction,1)
 if ride:
  c.rotate(tilt*direction)
  c.set_source_rgb(.12,.15,.18);c.rectangle(-8,-15,4,9);c.fill();c.rectangle(-7,-10,15,3);c.fill()
  c.set_source_rgb(.65,.68,.7);c.set_line_width(1.5);c.move_to(0,-7);c.line_to(0,-3);c.move_to(-7,-2);c.line_to(0,-4);c.line_to(7,-2);c.stroke()
  for xx in (-7,7):
   c.set_source_rgb(.06,.07,.08);c.arc(xx,-1,2,0,math.tau);c.fill()
   c.set_source_rgb(.7,.73,.75);c.set_line_width(.6);c.move_to(xx,-1);c.line_to(xx+math.cos(t*16)*1.5,-1+math.sin(t*16)*1.5);c.stroke()
  c.translate(0,-10)
 phase=t*10+seed
 c.rotate(math.sin(phase)*(.025 if slide else .055 if fall else .095))
 def oval(px,py,rx,ry,color,outline=False):
  c.save();c.translate(px,py);c.scale(rx,ry);c.arc(0,0,1,0,math.tau)
  c.set_source_rgb(*color)
  if outline:
   c.fill_preserve();c.set_source_rgb(.40,.43,.43);c.set_line_width(.12);c.stroke()
  else:c.fill()
  c.restore()
 black=(.035,.045,.045);white=(.97,.96,.88);gold=(1.,.69,.035)
 if slide:
  # Low, horizontal belly pose; feet trail behind and the head looks ahead.
  for i in range(3):
   age=(t*3+i*.33)%1
   c.set_source_rgba(*white,(1-age)*.28);c.set_line_width(.8)
   c.move_to(-12-age*14,-1-i*1.7);c.line_to(-8-age*14,-1-i*1.7);c.stroke()
  oval(-11,-4,4,1.8,gold);oval(-10,-7,3,1.5,gold)
  oval(-1,-6,11,5.5,black,True);oval(1,-3,9.2,2.8,white)
  oval(-3,-8,6.5,1.7,black,True)
  oval(8,-9,5,5.5,black,True)
  for px in (7,10):
   oval(px,-10,1.6,2.3,white);oval(px+.5,-9.7,.7,1.15,(.01,.015,.015))
  oval(13,-7,4.7,1.8,gold)
  c.restore();return
 # Broad webbed feet alternate beneath the belly.
 for side in (-1,1):
  stride=math.sin(phase+(math.pi if side<0 else 0))
  oval(side*4+stride*1.5,-1-(max(0,stride)*1.3 if not fall else 1),4.4,1.9,gold)
 # Flippers spread and flap during a fall, pendulum gently while waddling.
 for side in (-1,1):
  c.save();c.translate(side*5,-12)
  c.rotate(side*((1.05+math.sin(t*17)*.25) if fall else .25+math.sin(phase)*.2))
  oval(0,3,2.2,6,black,True);c.restore()
 oval(0,-10,7.2,10,black,True)
 oval(1,-8,5.3,7,white)
 oval(.3,-19,5.4,6,black,True)
 # White eye patches and a beak projecting in the walking direction.
 for px in (-1.7,2.4):
  oval(px,-20,1.9,2.8,white);oval(px+.55,-19.8,.85,1.35,(.01,.015,.015))
  oval(px+.8,-20.4,.3,.4,(1,1,1))
 c.set_source_rgb(*gold);c.move_to(0,-17);c.curve_to(3,-19,8,-18,8,-16)
 c.curve_to(6,-13,2,-13,-.3,-15);c.close_path();c.fill()
 c.set_source_rgba(.65,.31,0,.8);c.set_line_width(.6);c.move_to(1,-15.8);c.line_to(6.5,-16);c.stroke()
 oval(-1.3,-23.1,1.9,.65,(.22,.25,.24))
 c.restore()

def ambient_background(c,w,h,t):
 c.set_source_rgb(*rgb('background'));c.paint()
 # Quiet, free-moving atmosphere with no architecture or repeating tiles.
 for i in range(6):
  x=(i*w*.213+t*(8+i*2))%(w+240)-120
  y=h*(.22+.12*(i%4))+math.sin(t*.35+i*1.7)*8
  radius=70+(i%3)*35
  c.save();c.translate(x,y);c.scale(1,.22)
  glow=cairo.RadialGradient(0,0,0,0,0,radius)
  glow.add_color_stop_rgba(0,*rgb('cyan' if i%2 else 'blue'),.09)
  glow.add_color_stop_rgba(1,*rgb('cyan'),0)
  c.set_source(glow);c.arc(0,0,radius,0,math.tau);c.fill();c.restore()
 for i in range(max(18,int(w/35))):
  seed=i*2.39996
  x=(i*137.3+t*(9+7*math.sin(seed)))%(w+20)-10
  y=(i*37.7+t*(1.5+math.cos(seed)))%(h+12)-6
  y+=math.sin(t*.8+seed)*3
  twinkle=.10+.28*(.5+.5*math.sin(t*(.7+i%3*.23)+seed))**3
  c.set_source_rgba(*rgb('foreground' if i%4 else 'cyan'),twinkle)
  c.arc(x,y,.65+(i%3)*.25,0,math.tau);c.fill()
  if i%11==0:
   c.set_source_rgba(*rgb('cyan'),twinkle*.4);c.set_line_width(.7)
   c.move_to(x-3,y);c.line_to(x+3,y);c.move_to(x,y-3);c.line_to(x,y+3);c.stroke()

def catcher_art(c,w,h,t,angle=0):
 from catcher import PATHS,point
 panel(c,w,h,'bright_green')
 c.set_line_width(9);c.set_line_join(cairo.LINE_JOIN_MITER)
 c.set_source_rgb(*rgb('bright_green'))
 for path in PATHS:
  c.move_to(*point(*path[0],(0,0,w,h),angle))
  for xy in path[1:]:c.line_to(*point(*xy,(0,0,w,h),angle))
  c.stroke()
 hint(c,'DRAG / SCROLL TO ROTATE',h)


def portal_art(c,w,h,t,index,active=False):
 color=rgb('foreground' if index==0 else 'bright_green')
 cx,cy=w*.5,h*.5
 c.save();c.translate(cx,cy);c.scale(w*.30,h*.36)
 glow=cairo.RadialGradient(0,0,.4,0,0,1.4)
 glow.add_color_stop_rgba(0,*color,.04);glow.add_color_stop_rgba(.72,*color,.18 if active else .10);glow.add_color_stop_rgba(1,*color,.65);glow.add_color_stop_rgba(1.4,*color,0)
 c.set_source(glow);c.arc(0,0,1.4,0,math.tau);c.fill()
 for i in range(3):
  c.set_source_rgba(*color,.8-i*.18);c.set_line_width(.045)
  c.arc(0,0,1-i*.12,t*(1+i*.3)+i*2,t*(1+i*.3)+i*2+4.5);c.stroke()
 for i in range(10):
  angle=t*2+i*2.4;radius=.25+((t*.3+i*.17)%1)*.7
  c.set_source_rgba(*color,.7);c.arc(math.cos(angle)*radius,math.sin(angle)*radius,.025,0,math.tau);c.fill()
 c.restore()
 text(c,'A' if index==0 else 'B',12,23,11,'foreground' if index==0 else 'bright_green')

def draw_routes(c,routes,origin,t):
 ox,oy=origin
 for start,y,end in routes:
  if end<=start:continue
  start-=ox;end-=ox;y-=oy
  c.save();c.rectangle(start,y-BEAM_HALF_HEIGHT-2,end-start,2*BEAM_HALF_HEIGHT+4);c.clip()
  for lane in range(3):
   for i in range(int((end-start)/70)+2):
    x=start+(i*70+t*420+lane*23)%max(1,end-start);by=y+(lane-1)*BEAM_HALF_HEIGHT
    c.set_source_rgba(*rgb('yellow'),.2);c.set_line_width(2);c.move_to(x-15,by);c.line_to(x,by);c.stroke()
    c.set_source_rgb(*rgb('bright_yellow'));c.set_line_width(.7);c.move_to(x-7,by);c.line_to(x,by);c.stroke()
  c.restore()

def draw_splats(c,splats,now,origin):
 hx,hy=origin
 for n,(x,y,born) in enumerate(splats):
  age=now-born;px=x-hx;py=y-hy
  if not 0<=age<.9:continue
  for i in range(12):
   angle=i*2.4+n;radius=8+(i*13+n*7)%35
   sx=px+math.cos(angle)*radius;sy=py+math.sin(angle)*radius*.65
   c.set_source_rgba(*rgb('red'),.75*max(0,1-age/.9))
   c.arc(sx,sy,1+(i*3)%5,0,math.tau);c.fill()
   if age<.65:
    c.set_source_rgba(*rgb('red'),1-age/.65)
    c.rectangle(px+math.cos(angle)*age*135,py+math.sin(angle)*age*95+70*age*age,3,3);c.fill()

def draw_hazard(self,c,w,h,t):
 ambient_background(c,w,h,t);beam=h*.47
 heading(c,'SUPPRESSION FIELD','red')
 text(c,f'{self.colony.shot:03} intercepted',max(180,w-180),22,12,'red')
 hx,hy,_,_=self.hazard
 draw_splats(c,self.colony.splats,self.colony.effect_time,(hx,hy))
 routes=getattr(self,'routes',[(hx+MUZZLE_X,hy+beam,hx+w)])
 draw_routes(c,routes,(hx,hy),t)
 minigun(c,beam,t,h)
 hint(c,'SPACE pause / R reset',h)


_goal_image=None
def goal_art(c,w,h,data):
 global _goal_image
 if _goal_image is None:
  from pathlib import Path
  _goal_image=cairo.ImageSurface.create_from_png(str(Path(__file__).with_name('assets')/'omacon-2026.png'))
 panel(c,w,h,'bright_green')
 iw,ih=_goal_image.get_width(),_goal_image.get_height();scale=max(w/iw,h/ih)
 saved=data.get('saved',0);t=data.get('effect_time',0)
 c.save();c.translate((w-iw*scale)/2,(h-ih*scale)/2);c.scale(scale,scale);c.set_source_surface(_goal_image,0,0);c.paint_with_alpha(1 if saved else .65)
 if saved:
  c.set_operator(cairo.OPERATOR_ADD);c.paint_with_alpha(.2+.24*(.5+.5*math.sin(t*4)));c.set_operator(cairo.OPERATOR_OVER)
 c.restore()
 if saved:
  glow=cairo.RadialGradient(w*.5,h*.4,10,w*.5,h*.4,w*.65)
  glow.add_color_stop_rgba(0,1,.3,.95,.13+.12*(.5+.5*math.sin(t*4)));glow.add_color_stop_rgba(1,1,.2,.8,0)
  c.set_source(glow);c.paint()
 saved=data.get('saved',0);t=data.get('effect_time',0)
 # Soft pulsing pink light along all four edges; artwork stays edge-to-edge.
 pulse=(1.5+.6*math.sin(t*4)) if saved else .35
 for depth in range(28,0,-1):
  c.set_source_rgba(1,.35,.95,pulse*.012);c.set_line_width(depth)
  c.rectangle(0,0,w,h);c.stroke()
 c.set_source_rgba(1,.65,1,.65+.25*math.sin(t*2));c.set_line_width(2);c.rectangle(1,1,w-2,h-2);c.stroke()
 c.set_source_rgba(.03,.015,.08,.7);c.rectangle(10,h-23,145,17);c.fill()
 text(c,'WELCOME TO OMACON!' if saved else 'WAITING FOR YOU',17,h-11,10,'bright_green' if saved else 'foreground')
 ox,oy=data.get('goal',(0,0))[:2]
 for x,y,born in data.get('arrivals',[]):
  age=t-born
  for i in range(22):
   angle=i*2.4;v=35+(i*17)%80
   px=max(12,min(w-12,x-ox))+math.cos(angle)*v*age
   py=max(12,min(h-35,y-oy))+math.sin(angle)*v*age+40*age*age
   c.set_source_rgba(1,.5+(i%3)*.2,1 if i%2 else .45,max(0,1-age/1.5))
   c.rectangle(px,py,3,3);c.fill()

def barrier_art(c,w,h,barrier,window,apple=False):
 from brand_art import bliss,mac_frames,rainbow_wall,blue_screen,apple_surprises
 if not apple and getattr(barrier,'departed_at',None) is not None:
  blue_screen(c,w,h,barrier.time-barrier.departed_at)
  from destruction_art import fragments,chair_wreck
  fragments(c,barrier,window,False);chair_wreck(c,barrier,window)
  return
 if apple:mac_frames(c,w,h,None if barrier.departed_at is None else barrier.time-barrier.departed_at)
 else:bliss(c,w,h,barrier.time,not getattr(barrier,'rider',False))
 floor=h-20;left=barrier.rect(window)[0]-window[0];top=h-110
 heading(c,'APPLE / CLEAR THE WAY' if apple else 'WINDOWS / CLEAR THE WAY','foreground')
 # The walkable bridge remains after all four panes have shattered.
 c.set_source_rgb(*rgb('cyan'));c.rectangle(0,floor,w,3);c.fill()
 for i in range(0 if apple else 4):
  if barrier.health<=(3-i)/4:continue
  x=left+(i%2)*43;y=top+(i//2)*47
  c.set_source_rgb(*rgb('blue'));c.rectangle(x,y,37,41);c.fill()
  damage=(1-barrier.health)*4-int((1-barrier.health)*4)
  if damage>.15:
   c.set_source_rgba(*rgb('background'),.85);c.set_line_width(1.5)
   c.move_to(x+3,y+20);c.line_to(x+17,y+15);c.line_to(x+23,y+28);c.line_to(x+34,y+7);c.stroke()
 if apple:
  rainbow_wall(c,left,top,barrier.health)
  apple_surprises(c,w,h,barrier,window)
 if barrier.hit:
  for i in range(8):
   phase=(barrier.time*7+i*.17)%1
   c.set_source_rgba(*rgb('bright_yellow'),1-phase)
   c.rectangle(left-phase*30,top+45+math.sin(i*3)*phase*45,3,2);c.fill()
 from destruction_art import fragments
 fragments(c,barrier,window,apple)
 c.set_source_rgb(*rgb('dark_background'));c.rectangle(0,h-17,w,17);c.fill()
 hint(c,'PASSAGE OPEN' if barrier.health<=0 else ('AIM PORTAL FIRE AT THE WALL' if apple else 'TUX / CHAIR CRASH AHEAD'),h,'bright_green' if barrier.health<=0 else 'muted')


def source_art(c,w,h,d):
 panel(c,w,h,'bright_green')
 c.save();c.translate(14,38);c.scale(max(.1,(w-28)/900),max(.1,(h-100)/234))
 c.select_font_face('monospace',0,0);c.set_font_size(16)
 for col,row,ch,color in d.get('cells',[]):
  c.set_source_rgb(*color);c.move_to(col*10,16+row*13);c.show_text(ch)
 c.restore()
 heading(c,f'TUX / DEPARTURES / {d.get("total",1)-d.get("spawned",0):03} WAITING','foreground')
 c.set_source_rgb(*rgb('cyan'));c.set_line_width(3);c.move_to(0,h-20);c.line_to(w,h-20);c.stroke()
 hint(c,'CLICK / SPACE start · R reset',h)

"""Code-drawn nostalgic desktops for the two destructible gates."""
import math
import cairo

def rounded(c,x,y,w,h,r):
 c.new_sub_path()
 for cx,cy,a in ((x+w-r,y+r,-math.pi/2),(x+w-r,y+h-r,0),(x+r,y+h-r,math.pi/2),(x+r,y+r,math.pi)):
  c.arc(cx,cy,r,a,a+math.pi/2)
 c.close_path()

def bliss(c,w,h,t,chair=True):
 floor=h-20
 sky=cairo.LinearGradient(0,0,0,floor)
 sky.add_color_stop_rgb(0,.035,.29,.72);sky.add_color_stop_rgb(1,.48,.76,.98)
 c.set_source(sky);c.paint()
 for i in range(5):
  x=(w*(.12+i*.23)+t*(8+i*1.3))%(w+100)-40;y=42+(i%3)*15
  for dx,dy,r in ((-19,2,12),(0,-4,18),(21,1,13),(38,5,9)):
   c.save();c.translate(x+dx,y+dy);c.scale(1,.42);c.set_source_rgba(1,1,1,.75);c.arc(0,0,r,0,math.tau);c.fill();c.restore()
 hill=cairo.LinearGradient(0,floor*.55,0,floor)
 hill.add_color_stop_rgb(0,.37,.68,.08);hill.add_color_stop_rgb(.65,.25,.52,.045);hill.add_color_stop_rgb(1,.12,.35,.025)
 from terrain import hill_y
 c.move_to(0,hill_y(0,w,h))
 for px in range(0,int(w)+4,4):c.line_to(px,hill_y(px,w,h))
 c.line_to(w,floor);c.line_to(0,floor);c.close_path();c.set_source(hill);c.fill()
 # Uneven, sparse blades at the walking edge, with a slight breeze.
 for i in range(int(w/9)):
  x=(i*37.7)%w;length=2+(i*13)%6
  c.set_source_rgba(.65,.83,.23,.22);c.set_line_width(1)
  c.move_to(x,floor);c.line_to(x+math.sin(t*1.6+i)*2,floor-length);c.stroke()
 # A miniature office chair follows the actual hill curve, speeding downhill.
 u=.42+.56*((t/14)%1)**1.25
 px=w*(3*(1-u)**2*u*.2+3*(1-u)*u*u*.43+u**3*.66)
 py=floor*((1-u)**3*.78+3*(1-u)**2*u*.27+3*(1-u)*u*u*.40+u**3*.78)
 px=w*(.35+.5*((t/14)%1)**1.25);py=hill_y(px,w,h)
 c.save();c.translate(px if chair else -100,py-1);c.rotate(.08+u*.18+math.sin(t*7)*.04)
 c.set_source_rgb(.09,.11,.14);c.rectangle(-5,-21,9,10);c.fill();c.rectangle(-6,-11,14,3);c.fill()
 c.set_source_rgb(.6,.65,.69);c.set_line_width(1.4)
 c.move_to(-2,-16);c.line_to(-2,-9);c.line_to(1,-9);c.line_to(1,-3);c.stroke()
 c.move_to(-7,-2);c.line_to(1,-4);c.line_to(8,-2);c.stroke()
 for xx in (-7,1,8):
  c.set_source_rgb(.07,.08,.1);c.arc(xx,0,2,0,math.tau);c.fill()
  c.set_source_rgb(.65,.68,.7);c.set_line_width(.6);c.move_to(xx,0);c.line_to(xx+math.cos(t*9)*1.5,math.sin(t*9)*1.5);c.stroke()
 c.restore()
 c.set_source_rgba(.03,.12,.27,.65);c.rectangle(0,0,w,31);c.fill()

def mac_frames(c,w,h,exit_age=None):
 c.set_source_rgb(.08,.09,.14);c.paint()
 rounded(c,2,2,w-4,h-4,32);c.set_source_rgb(.12,.29,.54);c.fill()
 # Intentionally incompatible corner radii and offsets, as in the reference.
 rounded(c,9,34,w-18,h-37,11);c.set_source_rgb(.59,.64,.72);c.fill()
 rounded(c,12,37,w-24,h-43,27);c.set_source_rgb(.16,.18,.23);c.fill()
 c.save();rounded(c,12,37,w-24,h-43,27);c.clip()
 c.set_source_rgb(.22,.24,.3);c.rectangle(12,37,w-24,30);c.fill();c.restore()
 for x,color in ((31,(.96,.34,.32)),(51,(.98,.79,.25)),(71,(.36,.78,.37))):
  if exit_age is None:
   c.set_source_rgb(*color);c.arc(x,51,6,0,math.tau);c.fill()
  else:
   c.set_source_rgba(0,0,0,.3);c.arc(x,51,5,0,math.tau);c.fill()

def apple_path(c):
 c.move_to(40,20);c.curve_to(20,8,2,21,4,44);c.curve_to(5,63,19,88,30,87)
 c.curve_to(38,82,43,82,51,87);c.curve_to(62,91,74,69,78,60)
 c.curve_to(59,55,57,34,76,26);c.curve_to(65,12,51,14,40,20);c.close_path()
 c.move_to(40,15);c.curve_to(38,3,49,-5,59,-5);c.curve_to(60,5,49,15,40,15);c.close_path()

RAINBOW=((.38,.72,.24),(.98,.83,.17),(.96,.51,.14),(.88,.21,.26),(.57,.27,.61),(.19,.57,.82))
def rainbow_wall(c,left,top,health):
 if health<=0:return
 # The logo rises behind the wall, rather than being painted on its bricks.
 c.save();c.translate(left,top-18);apple_path(c);c.clip()
 for i,color in enumerate(RAINBOW):
  c.set_source_rgb(*color);c.rectangle(0,-6+i*16,82,16.5);c.fill()
 c.restore()
 wy=top+34
 for row in range(4):
  for col in range(4):
   x=left+col*24-(12 if row%2 else 0);y=wy+row*14
   lo=max(left,x);hi=min(left+80,x+23)
   if hi<=lo:continue
   if health<.5 and (row+col)%4==0:continue
   c.set_source_rgb(.37+.035*((row+col)%3),.20,.15);c.rectangle(lo,y,hi-lo,12);c.fill()
   c.set_source_rgba(.85,.58,.38,.22);c.rectangle(lo,y,hi-lo,2);c.fill()
 if health<.85:
  c.set_source_rgb(.08,.07,.08);c.set_line_width(2)
  c.move_to(left+45,wy);c.line_to(left+33,wy+15);c.line_to(left+44,wy+29);c.line_to(left+25,wy+54);c.stroke()


def blue_screen(c,w,h,age):
 from style import text
 c.set_source_rgb(.0,.32,.69);c.paint()
 text(c,':(',24,49,36)
 text(c,'Your penguin has left Windows.',24,78,14)
 text(c,'We ran into a freedom problem. No restart required.',24,100,11)
 text(c,f'{min(100,int(age*22)):02}% complete',24,124,11)
 text(c,'Stop code: TUX_HAS_LEFT_THE_BUILDING',24,h-19,10)


def apple_surprises(c,w,h,barrier,window):
 t=barrier.time;hit=getattr(barrier,'ball_hit_at',None)
 age=t-hit if hit is not None else 0
 if hit is None or age<4.5:
  radius=10;alpha=1 if hit is None else min(1,max(0,4.5-age))
  if hit is None:
   x=barrier.ball_x(window)-window[0];y=h-20-radius
  else:
   span=max(1,w-2*radius);travel=(barrier.ball_hit_x-radius+age*170)%(2*span)
   x=radius+(travel if travel<=span else 2*span-travel)
   y=h-20-radius-abs(math.sin(age*5))*55*math.exp(-age*.55)
  c.save();c.translate(x,y);c.rotate(t*3 if hit is None else t*12)
  colors=((1,.25,.25),(1,.65,.1),(1,.9,.2),(.35,.85,.35),(.15,.65,1),(.6,.3,.85))
  for i,color in enumerate(colors):
   c.move_to(0,0);c.arc(0,0,radius,i*math.tau/6,(i+1)*math.tau/6);c.close_path();c.set_source_rgba(*color,alpha);c.fill()
  c.restore()
  shine=cairo.RadialGradient(x-3,y-4,0,x,y,radius)
  shine.add_color_stop_rgba(0,1,1,1,.75*alpha);shine.add_color_stop_rgba(.45,1,1,1,.08*alpha);shine.add_color_stop_rgba(1,0,0,0,.25*alpha)
  c.set_source(shine);c.arc(x,y,radius,0,math.tau);c.fill()
 departed=getattr(barrier,'departed_at',None)
 if departed is not None:
  age=t-departed
  for i,color in enumerate(((.96,.34,.32),(.98,.79,.25),(.36,.78,.37))):
   local=max(0,age-i*.10)
   if local<2:
    x=31+i*20+(i-1)*35*local;y=51-65*local+190*local*local
    c.set_source_rgba(*color,min(1,2-local));c.arc(x,y,6,0,math.tau);c.fill()
    c.set_source_rgba(1,1,1,.4*min(1,2-local));c.arc(x-2,y-2,1.5,0,math.tau);c.fill()
  fade=min(1,max(0,(t-departed)*1.6))
  c.save();c.select_font_face('sans-serif',0,0);c.set_font_size(min(25,w/13))
  label='Think different.';ext=c.text_extents(label)
  c.set_source_rgba(1,1,.97,fade);c.move_to((w-ext.width)/2-ext.x_bearing,h*.55);c.show_text(label);c.restore()
  # A small rainbow Apple in the title bar sinks out of sight after the exit.
 logo_drop=0 if departed is None else min(32,(t-departed)*45)
 c.save();c.rectangle(w-34,4,25,27);c.clip();c.translate(w-33,8+logo_drop);c.scale(.22,.22);apple_path(c);c.clip()
 for i,color in enumerate(RAINBOW):c.set_source_rgb(*color);c.rectangle(0,-6+i*16,82,16.5);c.fill()
 c.restore()

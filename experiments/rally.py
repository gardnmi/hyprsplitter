"""Code-drawn rally coupe and desktop departure portals."""
import math
from pathlib import Path
import cairo
from experiments.theme import rgb, rgba
from experiments.visuals import ellipse, stroke

LOGO=cairo.ImageSurface.create_from_png(str(Path(__file__).parent/'platform-lab/assets/omarchy.png'))


def polygon(c,points,color):
 c.set_source_rgba(*color);c.move_to(*points[0])
 for point in points[1:]:c.line_to(*point)
 c.close_path();c.fill()


def quattro(c,x,floor,t,walking=False,falling=False,happy=False,lean=0,landing=0,phase=None):
 """Right-facing short-wheelbase rally Quattro, wheels grounded at floor."""
 phase=t*9 if phase is None else phase
 ellipse(c,x,floor+2,43,4,rgba('dark_background',.6 if not falling else .15))
 c.save();c.translate(x,floor-11)
 c.rotate((.12+math.sin(t*4)*.07) if falling else max(-.65,min(.65,lean)))
 bounce=math.sin(phase*2)*.7 if walking else math.sin(t*2)*.2
 c.translate(0,bounce+landing*3)
 # Exhaust pulses behind the rear bumper.
 if walking and not falling:
  for i in range(3):
   age=(t*2+i/3)%1
   ellipse(c,-45-age*18,-2-age*5,2+age*3,1+age*2,rgba('muted',.3*(1-age)))
 # Wing, sloping windscreen, boxy nose and flared rally arches.
 polygon(c,[(-44,-20),(-41,-29),(-33,-29),(-32,-19)],rgba('foreground'))
 polygon(c,[(-45,-29),(-29,-29),(-28,-25),(-45,-25)],rgba('red'))
 polygon(c,[(-44,0),(-44,-19),(-30,-23),(-20,-39),(11,-39),(28,-22),(43,-18),(46,-3),(38,3),(-36,3)],rgba('foreground'))
 polygon(c,[(-26,-24),(-17,-35),(-4,-35),(-4,-24)],rgba('dark_background'))
 polygon(c,[(-1,-35),(9,-35),(23,-23),(-1,-23)],rgba('dark_background'))
 polygon(c,[(1,-34),(8,-34),(19,-25),(8,-25)],rgba('blue',.65))
 stroke(c,[(-3,-36),(-3,-5)],rgba('muted',.65),1)
 stroke(c,[(-39,-15),(40,-15)],rgba('red'),5)
 polygon(c,[(-39,-12),(-25,-12),(-15,-1),(-29,-1)],rgba('orange'))
 polygon(c,[(-23,-12),(-16,-12),(-6,-1),(-13,-1)],rgba('red'))
 c.set_source_rgba(*rgba('dark_background'));c.rectangle(-8,-17,16,13);c.fill()
 c.set_source_rgba(*rgba('foreground'));c.select_font_face('monospace',0,1);c.set_font_size(10);c.move_to(-6,-7);c.show_text('01')
 stroke(c,[(-43,2),(43,2)],rgba('dark_background'),4)
 # Bright headlamp and front grille.
 polygon(c,[(35,-20),(43,-17),(43,-11),(35,-11)],rgba('bright_yellow'))
 stroke(c,[(44,-10),(45,-4)],rgba('muted'),3)
 for wx in (-27,28):
  ellipse(c,wx,1,12,12,rgba('dark_background'))
  ellipse(c,wx,1,8,8,rgba('muted'))
  ellipse(c,wx,1,5.5,5.5,rgba('foreground'))
  spin=phase*2 if walking else 0
  for i in range(5):
   a=spin+i*math.tau/5
   stroke(c,[(wx,1),(wx+math.cos(a)*5,1+math.sin(a)*5)],rgba('dark_background'),1.4)
  ellipse(c,wx,1,1.8,1.8,rgba('yellow'))
  stroke(c,[(wx-13,0),(wx-10,-9),(wx+9,-9),(wx+13,0)],rgba('foreground'),3)
 # Four tiny rings on the front quarter.
 for i in range(4):
  c.set_source_rgba(*rgba('muted'));c.set_line_width(.8);c.arc(25+i*3,-17,2,0,math.tau);c.stroke()
 c.restore()
 if landing>0:
  for i in range(6):
   age=1-landing
   ellipse(c,x-30+i*12+(i-2.5)*age*8,floor-age*9,2+age*4,2,rgba('yellow',landing*.4))
 if happy:
  for i in range(9):
   a=i*2.4;toss=(t*.6+i*.13)%1
   c.set_source_rgba(*rgba('green' if i%2 else 'yellow',1-toss));c.rectangle(x+math.sin(a)*toss*65,floor-35-toss*75,3,5);c.fill()


def portal(c,w,floor,t,brand,locked=False):
 """The OS mark itself is the gateway; no frame or doorway around it."""
 center=48 if brand!='omarchy' else w*.60
 color='red' if locked else 'accent' if brand=='omarchy' else 'blue' if brand=='windows' else 'foreground'
 # Light spills onto the ground beneath the mark.
 ellipse(c,center,floor-2,43 if brand!='omarchy' else min(80,w*.38),5,rgba(color,.12+.04*math.sin(t*2)))
 if brand=='omarchy':
  width=min(w-24,180);scale=width/LOGO.get_width()
  left=max(12,min(w-width-12,center-width/2));top=floor-LOGO.get_height()*scale-15
  c.save();c.translate(left,top);c.scale(scale,scale)
  c.set_source_rgba(*rgba(color));c.mask_surface(LOGO,0,0);c.restore()
  if not locked:
   for i in range(12):
    age=(t*.45+i*.137)%1
    x=left+((i*37)%max(1,int(width)))
    c.set_source_rgba(*rgba('accent',(1-age)*.5))
    c.rectangle(x,floor-8-age*82,2,2);c.fill()
 elif brand=='windows':
  # A large perspective Windows mark planted directly on the terrain.
  for col in range(2):
   for row in range(2):
    x=center-37+col*39;top=floor-91+row*43
    polygon(c,[(x,top+7-col*5),(x+34,top+2-col*5),(x+34,top+38-col*2),(x,top+38)],rgba('blue',.9))
 else:
  c.save();c.translate(center,floor-43);c.scale(1.65,1.65)
  c.set_source_rgba(*rgba('foreground'))
  c.move_to(0,-12);c.curve_to(-22,-25,-25,0,-16,15);c.curve_to(-9,27,-5,19,0,20)
  c.curve_to(6,18,12,28,19,12);c.curve_to(27,-5,18,-24,0,-12);c.fill()
  ellipse(c,5,-23,4,9,rgba('foreground'))
  ellipse(c,21,-6,9,10,rgba('background'))
  c.restore()

"""Shared vector characters: responsive animation without raster scaling."""
import math
import cairo
from experiments.theme import rgb, rgba, mix
from experiments.surfaces import height as surface_height


def ellipse(c,x,y,rx,ry,color):
 c.save();c.translate(x,y);c.scale(max(.01,rx),max(.01,ry));c.set_source_rgba(*color);c.new_path();c.arc(0,0,1,0,math.tau);c.fill();c.restore()


def stroke(c,points,color,width):
 c.set_source_rgba(*color);c.set_line_width(width);c.set_line_cap(cairo.LINE_CAP_ROUND);c.set_line_join(cairo.LINE_JOIN_ROUND)
 c.new_path();c.move_to(*points[0])
 for p in points[1:]:c.line_to(*p)
 c.stroke()


def _walker_vector(c,x,floor,t,walking=False,falling=False,happy=False,lean=0,landing=0,phase=None):
 """Stylized DHH: swept-back hair, stubble, grey hoodie and dark jacket."""
 phase=t*9 if phase is None else phase
 gait=1 if walking and not falling else 0
 bob=abs(math.sin(phase))*2.4*gait+math.sin(t*2)*.65*(1-gait)
 squash=max(0,landing)*5
 ellipse(c,x,floor+1,18 if not falling else 10,3,(.01,.025,.04,.28 if not falling else .08))
 c.save();c.translate(x,floor);c.rotate(max(-.18,min(.18,lean)))
 c.translate(0,squash-bob)
 for side in (-1,1):
  a=phase+(math.pi if side<0 else 0)
  footx=math.sin(a)*11*gait+side*5
  footy=-max(0,math.cos(a))*9*gait
  if falling:footx=side*(11+math.sin(t*12)*4);footy=-4
  knee=(footx*.45,-14-abs(footx)*.2)
  stroke(c,[(side*4,-26),knee,(footx,footy-4)],(*mix('blue','background',.6),1),7)
  stroke(c,[(footx-3,footy-2),(footx+5,footy-2)],rgba('dark_background'),6)
 # Navy jacket over a grey hoodie, with a zipper and drawstrings.
 stroke(c,[(-8,-43),(-9,-29)],(.14,.18,.23,1),10)
 stroke(c,[(0,-43),(0,-27)],(.12,.18,.23,1),19)
 stroke(c,[(-7,-46),(-4,-40),(3,-39),(8,-46)],(.56,.57,.55,1),5)
 stroke(c,[(0,-38),(0,-22)],(.43,.47,.48,1),1)
 for cord in (-4,5):stroke(c,[(cord,-40),(cord,-34)],(.79,.77,.69,1),1)
 for side in (-1,1):
  swing=-math.sin(phase)*side*8*gait
  hand=(side*12,-28+swing)
  if falling:hand=(side*18,-57+math.sin(t*15+side)*3)
  if happy:hand=(side*17,-58+math.sin(t*8)*3)
  stroke(c,[(side*7,-42),(side*12,-35+swing*.5),hand],(.17,.22,.27,1),6)
  ellipse(c,*hand,3.5,3.5,(1,.77,.54,1))
 # Hair silhouette extends behind the ears rather than a cartoon quiff.
 ellipse(c,-1,-61,14,17,(.20,.17,.14,1))
 ellipse(c,-11,-57,2,5,(.20,.17,.14,1))
 ellipse(c,11,-57,2,4,(.20,.17,.14,1))
 ellipse(c,0,-58,11.5,15,(.91,.71,.58,1))
 ellipse(c,-11,-56,2.5,4,(.84,.61,.48,1))
 # Swept-back crown and small receding temples.
 stroke(c,[(-12,-62),(-11,-70),(-7,-75),(0,-77),(8,-73),(12,-66)],(.21,.18,.15,1),5)
 for i in range(5):
  stroke(c,[(-9+i*4,-70+abs(i-2)),(-7+i*3,-74)],(.34,.29,.23,.7),1)
 # Stubble follows the jaw, leaving cheeks and mouth visible.
 ellipse(c,0,-49,9,5,(.30,.25,.21,.65))
 ellipse(c,2,-51,6,2.7,(.85,.64,.52,1))
 for i in range(13):
  a=i*math.pi/12
  ellipse(c,math.cos(a)*8,-49+math.sin(a)*4,.5,.6,(.25,.22,.19,.7))
 blink=(t%4.7)>4.54
 for ex in (-3,6):
  stroke(c,[(ex-2,-64),(ex+2,-64.5)],(.29,.23,.19,1),1.4)
  ellipse(c,ex,-60,1.8,.5 if blink else 1.8,(.75,.80,.78,1))
  if not blink:ellipse(c,ex+.6,-60,.9,1.3,(.19,.34,.38,1))
 stroke(c,[(2,-58),(3,-55),(1,-54)],(.72,.50,.39,.8),1)
 if falling:ellipse(c,3,-50,2.2,2.7,(.24,.17,.15,1))
 else:
  stroke(c,[(-1,-50),(5,-50 if not happy else -52)],(.35,.23,.20,1),1.2)
 # Narrow dark shades and a squared silhouette keep the tiny sprite readable.
 if not falling:
  stroke(c,[(-7,-61),(0,-61)],(.10,.12,.14,1),4)
  stroke(c,[(3,-61),(10,-61)],(.10,.12,.14,1),4)
  stroke(c,[(0,-61),(3,-61)],(.10,.12,.14,1),1.5)
 if falling:
  for i in range(3):stroke(c,[(-20+i*20,-94-i*7),(-20+i*20,-83-i*7)],(.65,.8,.92,.45),2)
 c.restore()
 if landing>0:
  for i in range(6):
   a=math.pi+i*math.pi/5;age=1-landing
   ellipse(c,x+math.cos(a)*(10+age*27),floor+math.sin(a)*age*13,2+age*2,1.5,(.65,.8,.75,landing*.4))
 if happy:
  for i in range(5):
   a=t*1.3+i*math.tau/5
   ellipse(c,x+math.cos(a)*27,floor-50+math.sin(a)*30,2,2,(1,.83,.36,.75))


def walker(c,x,floor,t,walking=False,falling=False,happy=False,lean=0,landing=0,phase=None):
 """Animated two-pixel sprite, rendered sharply rather than interpolated."""
 sprite=cairo.ImageSurface(cairo.FORMAT_ARGB32,48,64)
 sc=cairo.Context(sprite);sc.set_antialias(cairo.ANTIALIAS_NONE)
 sc.translate(24,54);sc.scale(.5,.5)
 _walker_vector(sc,0,0,t,walking,falling,happy,lean,landing,phase)
 c.save();c.translate(x-48,floor-108);c.scale(2,2)
 c.set_source_surface(sprite,0,0);c.get_source().set_filter(cairo.FILTER_NEAREST)
 c.paint();c.restore()


def grass(c,w,h,t,kind):
 for i in range(int(w/13)+1):
  x=5+i*13;y=surface_height(w,h,x,kind)
  gust=math.sin(t*2.2-x*.025)*3+math.sin(t*3.7+x*.06)
  for offset,length in ((-3,5),(0,9),(3,6)):
   stroke(c,[(x+offset,y),(x+offset+gust*.45,y-length*.55),(x+offset+gust,y-length)],rgba('green',.8),1.5)


def terrain(c,w,h,t,kind='platform',connected=False):
 c.set_source_rgb(*rgb('dark_background' if kind=='void' else 'background'));c.paint()
 # Discrete pixels and restrained terminal colors, instead of soft gradients.
 if kind not in ('hud','void'):
  c.set_source_rgb(*mix('background','foreground',.035));c.rectangle(0,0,w,35);c.fill()
  stroke(c,[(0,35),(w,35)],rgba('muted',.55),1)
  c.set_source_rgba(*rgb('muted'),.18)
  for i in range(12):
   x=int((i*97.31+t*(1+i%2))%max(1,w));y=int(55+(i*67.7)%max(1,h-150))
   c.rectangle(x,y,2,2)
  c.fill()
 floor=h-34
 if kind in ('hud','pad','weight'):return
 if kind=='void':return
 if kind=='water':
  c.set_source_rgb(*mix('blue','background',.7));c.rectangle(0,floor,w,34);c.fill()
  for row in range(3):
   points=[(x,floor+row*10+math.sin(x*.045-t*2.7+row)*2.5+math.sin(x*.08+t*1.5)*1.2) for x in range(0,int(w)+4,3)]
   stroke(c,points,rgba('cyan' if row==0 else 'blue',.9-row*.2),2)
  return
 if kind in ('mud','fast','hill'):
  points=[(x,round(surface_height(w,h,x,kind)/2)*2) for x in range(0,int(w)+5,4)]
  points[-1]=(w,surface_height(w,h,w,kind))
  c.set_source_rgb(*({'mud':mix('brown','background',.25),'fast':mix('cyan','background',.75),'hill':mix('green','background',.65)}[kind]))
  c.move_to(0,h)
  for x,y in points:c.line_to(x,y)
  c.line_to(w,h);c.close_path();c.fill()
  stroke(c,points,{'mud':rgba('yellow'),'fast':rgba('cyan'),'hill':rgba('green')}[kind],4)
  if kind=='mud':
   ripples=[(x,floor+math.sin(x*.06+t*2)*1.5) for x in range(0,int(w)+4,3)]
   stroke(c,ripples,rgba('yellow',.7),3)
   for i in range(int(w/48)):
    x=24+i*48
    age=(t*.5+i*.37)%1
    ellipse(c,x+math.sin(t+i)*3,floor+12,10+math.sin(t*2+i)*4,3+math.sin(t*2+i),(*rgb('brown'),.8))
    ellipse(c,x+4,floor+8-age*4,2+math.sin(age*math.pi)*3,1+math.sin(age*math.pi)*2,(*rgb('yellow'),.6*(1-age)))
    stroke(c,[(x-8-age*8,floor+14),(x+8+age*8,floor+14)],rgba('yellow',.3*(1-age)),1)
  elif kind=='fast':
   for i in range(int(w/45)+2):
    x=(i*45+t*75)%max(1,w)
    stroke(c,[(x-4,floor+10),(x+3,floor+15),(x-4,floor+20)],rgba('cyan',.75),2)
  else:
   grass(c,w,h,t,kind)
  return
 c.set_source_rgb(*rgb('dark_background'));c.rectangle(0,floor,w,34);c.fill()
 c.set_source_rgba(*rgb('muted'),.25)
 for row in range(2):
  for col in range(int(w/16)+1):c.rectangle(col*16+row*8,floor+9+row*12,2,2)
 c.fill()
 edge=rgba('green') if connected else rgba('accent')
 stroke(c,[(0,floor),(w,floor)],edge,4)
 for i in range(int(w/29)+1):
  stroke(c,[(i*29+5,floor+13),(i*29+17,floor+13)],rgba('muted',.5),2)
 grass(c,w,h,t,'flat')
 for x in (7,w-7):
  c.set_source_rgba(*edge);c.rectangle(x-3,floor-3,6,6);c.fill()


def cloud(c,w,h,t,wet=False,motion=0):
 """Soft POC-style cloud with drag surprise, blinking and a happy rain face."""
 c.save();c.scale(w/320,h/220)
 bob=math.sin(t*1.5)*3;tilt=max(-.10,min(.10,motion*.005))
 c.translate(160,85+bob);c.rotate(tilt);c.translate(-160,-85)
 glow=cairo.RadialGradient(160,85,8,160,85,115)
 glow.add_color_stop_rgba(0,.2,.6,.9,.18);glow.add_color_stop_rgba(1,.1,.3,.8,0)
 c.set_source(glow);c.rectangle(20,0,280,180);c.fill()
 for x,y,r in ((103,88,29),(137,68,36),(178,70,40),(215,90,29),(160,96,33)):
  ellipse(c,x,y,r,r,(.76,.87,.96,1))
 blink=t%4.4>4.24
 look=max(-3,min(3,motion*.12))
 for x in (145,175):
  ellipse(c,x+look,88,3,.7 if blink else 3.5,(.10,.20,.30,1))
  if wet:ellipse(c,x-5,99,5,2,(.94,.56,.57,.28))
 if abs(motion)>8:ellipse(c,160,101,4,5,(.1,.2,.3,1))
 else:
  c.set_source_rgb(.1,.2,.3);c.set_line_width(2);c.new_path();c.arc(160,95,9 if wet else 7,.15,math.pi-.15);c.stroke()
 c.restore()

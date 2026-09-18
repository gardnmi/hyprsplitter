"""Chunky pixel minigun with a feeding belt and ejected brass."""
import math
import cairo


GUN_SCALE = .9  # Three times the small version; 30% of the original.
MUZZLE_X = 12 + 86 * GUN_SCALE
BEAM_HALF_HEIGHT = 3.6

def minigun(c,beam,t,height):
 c.save();c.set_antialias(cairo.ANTIALIAS_NONE)
 c.translate(12,beam-13.5*GUN_SCALE);c.scale(GUN_SCALE,GUN_SCALE)
 steel=(.36,.37,.38);dark=(.23,.24,.25);shadow=(.12,.13,.14)
 gold=(1,.75,.03);light=(1,.91,.22)
 def block(x,y,w,h,color):
  c.set_source_rgb(*color);c.rectangle(x,y,w,h);c.fill()
 recoil=0
 c.translate(recoil,0)
 # Rear grip and stepped receiver silhouette.
 block(0,7,3,9,steel);block(2,1,3,7,dark)
 for i in range(4):block(3+i,2+i*2,3,1,shadow)
 block(2,13,15,3,steel)
 block(16,9,4,8,steel);block(18,6,4,13,steel)
 block(21,4,18,17,steel);block(39,5,11,15,dark)
 block(25,7,10,8,shadow)
 # Top carry handle, rear grip and mounting post.
 block(31,-4,3,8,steel);block(30,-5,3,2,steel)
 block(21,-8,13,2,dark);block(21,-8,2,4,dark);block(32,-8,2,4,dark)
 for i in range(4):block(23+i*3,-8,1,2,steel)
 # Long barrel cluster and heavy retaining collars.
 block(49,7,29,13,shadow)
 for i in range(3):
  y=8+i*4
  shade=steel if (int(t*24)+i)%3 else dark
  block(50,y,27,2,shade)
 block(61,6,4,15,dark);block(76,5,4,17,dark);block(80,7,6,13,steel)
 block(80,10,6,2,shadow);block(80,15,6,2,shadow)
 # Belt links feed upward into the receiver. Shell tips point right.
 phase=(t*16)%4
 for i in range(6):
  y=9+i*4-phase
  if y<8:continue
  block(27,y+2,4,3,dark)
  block(25,y,7,3,light);block(30,y,3,3,gold);block(33,y+1,1,1,gold)
 # Pixel muzzle flame pulses directly at the barrel tips.
 reach=4+int(abs(math.sin(t*77))*8)
 block(86,9,4,9,gold);block(90,11,reach,5,light)
 block(88,7,4,2,gold);block(88,18,5,2,gold)
 c.restore()
 # Casings eject beside the feed port, arc outward and bounce on the floor.
 for i in range(12):
  age=(t*1.1+i/12)%1;elapsed=age*.95
  x=12+25*GUN_SCALE-elapsed*(24+i%3*6)
  y=beam-3-24*elapsed+100*elapsed*elapsed
  floor=height-19
  if y>floor:
   y=floor-abs(math.sin((y-floor)*.16))*max(0,6*(1-age));x+=age*8
  c.save();c.translate(x,y);c.rotate(elapsed*(9+i%4));c.scale(.3,.3)
  c.set_antialias(cairo.ANTIALIAS_NONE)
  c.set_source_rgba(*gold,1-age*.6);c.rectangle(-5,-2,10,4);c.fill()
  c.set_source_rgba(*light,1-age*.6);c.rectangle(-5,-2,7,1);c.fill()
  c.set_source_rgba(.45,.29,.06,1-age*.6);c.rectangle(-5,-2,1,4);c.fill();c.restore()

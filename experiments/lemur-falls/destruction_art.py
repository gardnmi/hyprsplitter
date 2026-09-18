"""Spinning glass shards and weighty brick chunks, with short impact flashes."""
import math
from brand_art import RAINBOW

def fragments(c,barrier,window,apple):
 c.new_path()
 for bx,by,born,index in barrier.bursts:
  age=barrier.time-born
  if not 0<=age<1.6:continue
  x=bx-window[0];y=by-window[1];fade=min(1,(1.6-age)*2)
  if age<.13:
   c.set_source_rgba(1,.85,.5,(1-age/.13)*.8);c.arc(x,y,9+age*140,0,math.tau);c.fill()
  if index==0:
   c.set_source_rgba(1,.75,.45,max(0,.6-age));c.set_line_width(2);c.arc(x,y,10+age*95,0,math.tau);c.stroke()
  for i in range(28 if index==0 else 16):
   angle=i*2.399+index;speed=40+(i*37)%150
   px=x+math.cos(angle)*speed*age;py=y+math.sin(angle)*speed*age-65*age+210*age*age
   c.save();c.translate(px,py);c.rotate(angle+age*(i%7-3)*3)
   if apple:
    color=RAINBOW[i%6] if i%4==0 else (.36+(i%3)*.08,.19+(i%2)*.04,.12)
    c.set_source_rgba(*color,fade);c.rectangle(-5,-3,10+(i%3)*2,6);c.fill()
    c.set_source_rgba(.9,.66,.4,fade*.5);c.rectangle(-5,-3,10,1);c.fill()
   else:
    c.move_to(-4,-6);c.line_to(6,2);c.line_to(-2,5);c.close_path()
    c.set_source_rgba(.35+(i%3)*.16,.65+(i%2)*.12,1,fade*.9);c.fill_preserve()
    c.set_source_rgba(.85,.96,1,fade*.85);c.set_line_width(.8);c.stroke()
   c.restore()
  # A low dust puff from the last brick/pane, fading completely.
  if index==0:
   for i in range(8):
    c.set_source_rgba(*((.6,.4,.28) if apple else (.5,.75,1)),max(0,.18-age*.2))
    c.arc(x+(i-3.5)*age*25,y+18+age*12,3+age*14,0,math.tau);c.fill()


def chair_wreck(c,barrier,window):
 crash=getattr(barrier,'chair_crash',None)
 if crash is None:return
 x,y,born=crash;age=barrier.time-born
 if not 0<=age<1.6:return
 c.save();c.translate(x-window[0]-age*42,y-window[1]-80*age+150*age*age)
 c.rotate(-age*9);c.set_source_rgba(.6,.65,.7,min(1,(1.6-age)*2))
 c.set_line_width(3);c.move_to(0,-6);c.line_to(0,5);c.move_to(-9,8);c.line_to(0,3);c.line_to(9,8);c.stroke()
 c.set_source_rgba(.12,.15,.2,min(1,(1.6-age)*2));c.rectangle(-10,-11,20,5);c.rectangle(-11,-24,5,15);c.fill()
 for xx in (-9,9):c.arc(xx,8,3,0,math.tau);c.fill()
 c.restore()

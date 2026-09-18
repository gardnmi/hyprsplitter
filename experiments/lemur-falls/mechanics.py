"""Desktop-space bridge sockets, batch launcher and community elevator."""
import math

class Journey:
 roles=('plugin2','plugin3','elevator')
 def __init__(self,mx,my,mw,mh,goal):
  self.rects={'plugin2':(mx+mw*.54,my+mh-245,56,38),'plugin3':(mx+mw*.59,my+mh-245,56,38),'elevator':(mx+mw*.37,goal[1],360,my+mh-90)}
  self.reset()
 def reset(self):
  self.progress=0.;self.docked=set()
 def sockets(self):
  x,y,w,h=self.rects['elevator']
  return [(x+35,y+h-65),(x+w-35,y+h-65)]
 def docking(self):
  self.docked=set()
  for sx,sy in self.sockets():
   candidates=[(math.hypot(r[0]+r[2]/2-sx,r[1]+r[3]/2-sy),name) for name,r in self.rects.items() if name in ('plugin2','plugin3') and name not in self.docked]
   if candidates:
    distance,name=min(candidates)
    if distance<58:self.docked.add(name)
 def lift(self):
  x,y,w,h=self.rects['elevator']
  return x,y+h-110-self.progress*(h-280),w
 def ledges(self):
  return [self.lift()]
 def step(self,dt,colony):
  self.docking();old=self.lift()[1]
  target=len(self.docked)/2
  self.progress+=max(-dt*.22,min(dt*.22,target-self.progress))
  delta=self.lift()[1]-old
  for a in colony.lemurs:
   if a.room==3:a.y+=delta

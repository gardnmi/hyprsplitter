"""World-space ramp launch and swept landing physics."""
import math


def sun_target(rect):
 x,y,w,h=rect
 return x+w*.56,y+h*.48,min(w,h)*.12

def landing_target(rect):
 x,y,w,h=rect
 return x+w*.55,y+landing_y(w,h,w*.55),36.

def segment_distance(ax,ay,bx,by,x,y):
 dx,dy=bx-ax,by-ay
 u=max(0,min(1,((x-ax)*dx+(y-ay)*dy)/max(1e-9,dx*dx+dy*dy)))
 return math.hypot(ax+u*dx-x,ay+u*dy-y)

def crosses_panel(ax,ay,bx,by,rect):
 x,y,w,h=rect;lo,hi=0.,1.
 for start,delta,minimum,maximum in ((ax,bx-ax,x,x+w),(ay,by-ay,y,y+h)):
  if abs(delta)<1e-9:
   if not minimum<=start<=maximum:return False
  else:
   a,b=sorted(((minimum-start)/delta,(maximum-start)/delta))
   lo=max(lo,a);hi=min(hi,b)
   if lo>hi:return False
 return True

def ramp_y(w,h,x,rise=90):
 return h-42-max(0,min(1,(x-w*.38)/(w*.5)))*rise


def landing_y(w,h,x):
 """Descending catch ramp, followed by a short flat runout."""
 return h-42-90*(1-max(0,min(1,x/(w*.85))))


def landing_slope(w,h,x):
 return (landing_y(w,h,x+1)-landing_y(w,h,x-1))/2


def landing_hit(ox,oy,nx,ny,rect):
 """Find the feet's first crossing of the ramp within its usable width."""
 x,y,w,h=rect
 if ny<=oy or nx<=ox:return None
 start=max(0,(x+15-ox)/(nx-ox));end=min(1,(x+w-15-ox)/(nx-ox))
 if start>end:return None
 def distance(t):
  return oy+(ny-oy)*t-y-landing_y(w,h,ox+(nx-ox)*t-x)
 if distance(start)>0 or distance(end)<0:return None
 for _ in range(24):
  mid=(start+end)/2
  if distance(mid)<0:start=mid
  else:end=mid
 hit=ox+(nx-ox)*end
 return hit,y+landing_y(w,h,hit-x)


class Jump:
 def __init__(self,rise=90):
  self.rise=rise
  self.state='ready';self.charge=0.;self.x=65.;self.y=0.;self.vx=0.;self.vy=0.;self.sun=False;self.trail=[];self.local=65.
  self.airtime=0.;self.sun_accuracy=0.;self.landing_accuracy=0.;self.perfect=False;self.score=0;self.result_age=0.;self.sun_pulse=0.;self.fireworks=False;self.firework_age=0.
 def release(self):
  if self.state=='charging':self.state='runup';self.power=self.charge;self.speed=330+460*self.power
 def step(self,dt,g):
  if self.fireworks:self.firework_age+=dt
  self.sun_pulse=max(0,self.sun_pulse-dt)
  if self.state in ('landed','missed'):self.result_age+=dt
  rx,ry,rw,rh=g['ramp'];lx,ly,lw,lh=g['landing']
  if self.state in ('ready','charging'):
   if self.state=='charging':self.charge=min(1,self.charge+dt/1.6)
   self.x=rx+65;self.y=ry+ramp_y(rw,rh,65,self.rise)
  elif self.state=='runup':
   self.local+=self.speed*dt;self.x=rx+self.local;self.y=ry+ramp_y(rw,rh,self.local,self.rise)
   if self.local>=rw*.88:
    self.x=rx+rw*.88;self.y=ry+ramp_y(rw,rh,rw*.88,self.rise)
    angle=math.atan2(self.rise,rw*.5);self.vx=self.speed*math.cos(angle);self.vy=-self.speed*math.sin(angle);self.state='flying'
  elif self.state=='flying':
   ox,oy=self.x,self.y;self.vy+=500*dt;self.x+=self.vx*dt;self.y+=self.vy*dt
   self.airtime+=dt
   sx,sy,radius=sun_target(g['sky'])
   distance=segment_distance(ox,oy-20,self.x,self.y-20,sx,sy)
   if crosses_panel(ox,oy-16,self.x,self.y-16,g['sky']) and not self.fireworks:self.fireworks=True;self.firework_age=0.
   self.sun_accuracy=max(self.sun_accuracy,max(0,1-distance/radius))
   if distance<=radius and not self.sun:self.sun=True;self.sun_pulse=1.

   contact=landing_hit(ox,oy,self.x,self.y,g['landing'])
   if contact:
     hit,ground=contact
     self.x=hit;self.y=ground;self.local=hit-lx;self.state='landed';self.touchdown_local=self.local;self.vx*=.55
     target,_,half=landing_target(g['landing'])
     error=abs(hit-target);self.perfect=error<=half
     self.landing_accuracy=max(0,1-error/(lw*.55))
     self.score=round(1000+1000*self.sun_accuracy+min(500,self.airtime*200)+1000*self.landing_accuracy+(500 if self.perfect else 0))
   if self.y>max(v[1]+v[3] for v in g.values())+160:self.state='missed'
  elif self.state=='landed':
   self.vx=max(0,self.vx-550*dt);self.local=min(lw-45,self.local+self.vx*dt)
   self.x=lx+self.local;self.y=ly+landing_y(lw,lh,self.local)
  if self.state=='flying':
   self.trail.append((self.x,self.y-12));self.trail=self.trail[-20:]
  elif self.trail:self.trail.pop(0)

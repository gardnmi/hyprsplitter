"""A shootable Windows gate; the surviving panes form one blocking wall."""
class Barrier:
 def __init__(self):
  self.health=1.;self.hit=False;self.bursts=[];self.time=0.;self.departed_at=None;self.ball_hit_at=None;self.ball_hit_x=None
 def rect(self,window):
  x,y,w,h=window
  return x+w-104,y+h-110,80,90
 def step(self,dt,routes,window):
  self.time+=dt;self.hit=False;self.bursts=[b for b in self.bursts if self.time-b[2]<1.6]
  if self.health<=0:return routes
  x,y,w,h=self.rect(window);result=[]
  for start,beam,end in routes:
   if y<=beam<=y+h and start<x+w and end>=x:
    result.append((start,beam,max(start,x)));self.hit=True
   else:result.append((start,beam,end))
  if self.hit:
   before=self.health;self.health=max(0,self.health-dt/3.)
   for threshold in (.75,.5,.25,0):
    if before>threshold>=self.health:self.bursts.append((x+w/2,y+h/2,self.time,int(threshold*4)))
  return result

 def chair_impact(self,actors,window,lift):
  if self.health<=0:return False
  bx,by,bw,bh=self.rect(window)
  for a in actors:
   if a.room!=1 or a.state!='walk' or a.x<bx-8:continue
   self.health=0.;self.departed_at=self.time
   self.bursts.append((bx+bw/2,by+bh/2,self.time,0))
   self.chair_crash=(a.x,a.y,self.time)
   # A short ballistic hop carries Tux clear of the wreck onto the lift.
   lx,ly,lw=lift;duration=.9
   a.room=None;a.state='fall';a.drop=a.y;a.tilt=0.
   a.flight_vx=(lx+min(60,lw*.2)-a.x)/duration
   a.vy=(ly-a.y-300*duration*duration)/duration
   return True
  return False

 def observe_exit(self,previous_rooms,actors,room=1):
  if self.departed_at is None and any(old==room and a.room!=room and a.state!='lost' for old,a in zip(previous_rooms,actors)):
   self.departed_at=self.time

 def ball_x(self,window):
  import math
  return window[0]+window[2]*.38+math.sin(self.time*.65)*18
 def observe_apple(self,previous_rooms,previous_x,actors,window):
  self.observe_exit(previous_rooms,actors,room=2)
  if self.ball_hit_at is not None:return
  bx=self.ball_x(window)
  for old,ox,a in zip(previous_rooms,previous_x,actors):
   if a.state not in ('lost','saved') and a.room==2 and min(ox,a.x)-18<=bx<=max(ox,a.x)+18:
    self.ball_hit_at=self.time;self.ball_hit_x=bx-window[0];break

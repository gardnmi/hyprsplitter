"""One hundred walkers, gravity, movable ledges and a safe exit."""
from dataclasses import dataclass
from portals import intersection,core,center

@dataclass
class Lemur:
 x:float
 y:float
 speed:float
 vy:float=0
 room:int|None=None
 drop:float=0
 state:str='fall'
 cooldown:float=0.
 teleports:int=0
 caught:bool=False
 flight_vx:float|None=None
 tilt:float=0.

class Colony:
 def __init__(self,total=100):
  self.total=total
  self.lemurs=[];self.time=0.;self.running=False;self.saved=0;self.lost=0;self.spawned=0;self.bursts=[];self.splats=[];self.shot=0;self.effect_time=0.;self.arrivals=[]
 def step(self,dt,ledges,source=(420,200),bottom=700,exit_room=-1,hazard=None,hazards=None,portals=(),left_rooms=(),soft_rooms=(),catcher=None,goal=None,blockers=(),waiting_rooms=(),windows_terrain=None):
  self.effect_time+=dt
  self.arrivals=[s for s in self.arrivals if self.effect_time-s[2]<1.5]
  self.splats=[s for s in self.splats if self.effect_time-s[2]<.9]
  if not self.running:return
  self.time+=dt
  while self.spawned<self.total and self.time>=self.spawned*.12:
   i=self.spawned;self.lemurs.append(Lemur(source[0]+(i%5-2)*3,source[1],64+(i*7)%23,drop=source[1]));self.spawned+=1
  for a in self.lemurs:
   if a.state in ('saved','lost'):continue
   a.cooldown=max(0,a.cooldown-dt)
   if a.room is not None:
    x,y,w=ledges[a.room];ox,oy=a.x,a.y
    multiplier=1.
    if a.room==1 and windows_terrain:
     from terrain import slope
     multiplier=max(.7,min(2.8,1.25+slope(a.x,windows_terrain)*3))
    a.x+=a.speed*dt*multiplier;a.y=y
    if a.room in waiting_rooms:a.x=max(x+12,min(x+w*.55,a.x))
    for bx,by,bw,bh in blockers:
     if by<a.y and a.y-24<by+bh:
      if ox<=bx-8<a.x:a.x=bx-8
      elif ox>=bx+bw+8>a.x:a.x=bx+bw+8
    if a.room==1 and windows_terrain:
     from terrain import ground,slope
     import math
     a.y=ground(a.x,windows_terrain);a.tilt=math.atan(slope(a.x,windows_terrain))
    if any(intersection(ox,oy,a.x,a.y,(hx-7,hy,hw+14,hh+24)) is not None for hx,hy,hw,hh in (hazards if hazards is not None else [hazard] if hazard else [])):
     a.state='lost';self.lost+=1;self.shot+=1;self.splats.append((a.x,a.y,self.effect_time));continue
    if goal and intersection(ox,oy-12,a.x,a.y-12,goal) is not None:
     self.rescue(a);continue
    if self.transit(a,ox,oy,portals):continue
    if exit_room is not None and a.room==(len(ledges)-1 if exit_room==-1 else exit_room) and a.x>=x+w-30:
     a.state='saved';self.saved+=1;continue
    if a.x>x+w or a.x<x:
     neighbor=next((j for j,(nx,ny,nw) in enumerate(ledges) if j!=a.room and abs(ny-y)<3 and nx-2<=a.x<=nx+nw+2),None)
     if neighbor is not None:a.room=neighbor;a.y=ledges[neighbor][1];continue
     a.room=None;a.state='fall';a.drop=a.y;a.vy=0
   else:
    ox,oy=a.x,a.y;a.vy+=600*dt;a.x+=(a.flight_vx if a.flight_vx is not None else a.speed*.4)*dt;a.y+=a.vy*dt
    danger=[]
    for hx,hy,hw,hh in (hazards if hazards is not None else [hazard] if hazard else []):
     hit=intersection(ox,oy,a.x,a.y,(hx-7,hy,hw+14,hh+24))
     if hit is not None:danger.append(hit)
    impact=min(danger) if danger else None
    arrival=intersection(ox,oy-12,a.x,a.y-12,goal) if goal else None
    first=min(v for v in (impact,arrival) if v is not None) if impact is not None or arrival is not None else None
    if self.transit(a,ox,oy,portals,first):continue
    if arrival is not None and (impact is None or arrival<impact):
     a.x=ox+(a.x-ox)*arrival;a.y=oy+(a.y-oy)*arrival
     self.rescue(a);continue
    if impact is not None:
     a.x=ox+(a.x-ox)*impact;a.y=oy+(a.y-oy)*impact
     a.state='lost';self.lost+=1;self.shot+=1
     self.splats.append((a.x,a.y,self.effect_time));continue
    for bx,by,bw,bh in blockers:
     if by<a.y and a.y-24<by+bh:
      if ox<=bx-8<a.x:a.x=bx-8
      elif ox>=bx+bw+8>a.x:a.x=bx+bw+8
    if catcher:
     from catcher import resolve
     resolve(a,ox,oy,dt,*catcher)
    hits=[]
    for i,(x,y,w) in enumerate(ledges):
     if i==1 and windows_terrain and a.y>oy:
      from terrain import ground
      if oy<=ground(ox,windows_terrain) and a.y>=ground(a.x,windows_terrain):
       lo,hi=0.,1.
       for _ in range(12):
        f=(lo+hi)/2;hx=ox+(a.x-ox)*f
        if oy+(a.y-oy)*f>=ground(hx,windows_terrain):hi=f
        else:lo=f
       hx=ox+(a.x-ox)*hi
       if x<=hx<=x+w:hits.append((ground(hx,windows_terrain),i,hx))
      continue
     if oy<=y<=a.y and a.y>oy:
      f=(y-oy)/(a.y-oy);hx=ox+(a.x-ox)*f
      if x<=hx<=x+w:hits.append((y,i,hx))
    if hits:
     y,i,hx=min(hits);a.x=hx;a.y=y
     if y-a.drop>245 and i not in soft_rooms:a.state='lost';self.lost+=1;self.bursts.append((a.x,a.y,self.time))
     else:
      a.room=i;a.state='walk';a.vy=0;a.flight_vx=None
      a.speed=-abs(a.speed) if i in left_rooms else abs(a.speed)
    elif a.y>bottom+25:a.state='lost';self.lost+=1;self.bursts.append((a.x,bottom-10,self.time))
  self.bursts=[b for b in self.bursts if self.time-b[2]<.7]
  if self.saved+self.lost==self.total:self.running=False

 def rescue(self,a):
  a.state='saved';a.room=None;self.saved+=1;self.arrivals.append((a.x,a.y,self.effect_time))

 def transit(self,a,ox,oy,portals,impact=None):
  if len(portals)!=2 or a.cooldown>0:return False
  hits=[]
  for i,p in enumerate(portals):
   hit=intersection(ox,oy-14,a.x,a.y-14,core(p))
   if hit is not None and (impact is None or hit<=impact):hits.append((hit,i))
  if not hits:return False
  _,i=min(hits);out=portals[1-i];cx,cy=center(out)
  a.x=cx+out[2]*.20+10;a.y=cy+14;a.room=None;a.state='fall'
  a.vy=min(a.vy,180);a.flight_vx=None;a.drop=a.y;a.cooldown=.4;a.teleports+=1
  return True

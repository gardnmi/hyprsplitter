"""Walker handoff across real platform-window edges."""
from experiments.surfaces import height, slope, speed

FLOOR = 34
TOLERANCE = 22


def ground(rect,local_x=0,kind="flat"):
    x,y,w,h=rect
    return y+height(w,h,local_x,kind)


def neighbor(room, geometry, surfaces=None):
    surfaces=surfaces or {}
    r=geometry[room]; right=r[0]+r[2]
    candidates=[k for k,v in geometry.items() if k!=room
                and abs(v[0]-right)<=TOLERANCE and abs(ground(v,0,surfaces.get(k,"flat"))-ground(r,r[2],surfaces.get(room,"flat")))<=TOLERANCE]
    return min(candidates,key=lambda k:abs(geometry[k][0]-right)) if candidates else None


class Walker:
    def __init__(self):
        self.room='start';self.x=38.;self.running=False;self.won=False
        self.waiting=False;self.visited={'start'}
        self.falling=False;self.dead=False;self.world_x=0.;self.world_y=0.;self.vy=0.;self.speed=90.

    def step(self,dt,geometry,exit_open=True,blocker=None,bottom=2000,surfaces=None):
        surfaces=surfaces or {}
        if not self.running or self.won or self.dead:return
        if self.falling:
            # Sweep the feet along the whole frame, not just its endpoint.
            # Small horizontal intervals also resolve curved hill surfaces.
            import math
            old_x,old_y=self.world_x,self.world_y
            self.vy+=900*dt
            end_x=old_x+90*dt;end_y=old_y+self.vy*dt
            steps=max(1,math.ceil(max(abs(end_x-old_x),abs(end_y-old_y))/2))
            landed=False
            for i in range(1,steps+1):
                a=(i-1)/steps;b=i/steps
                x0=old_x+(end_x-old_x)*a;y0=old_y+(end_y-old_y)*a
                x1=old_x+(end_x-old_x)*b;y1=old_y+(end_y-old_y)*b
                hits=[]
                for k,r in geometry.items():
                    if x1<r[0] or x0>r[0]+r[2]:continue
                    kind=surfaces.get(k,"flat")
                    d0=y0-ground(r,x0-r[0],kind);d1=y1-ground(r,x1-r[0],kind)
                    if d0<=0<=d1:
                        fraction=-d0/max(1e-9,d1-d0)
                        hit_x=x0+(x1-x0)*fraction
                        if r[0]<=hit_x<=r[0]+r[2]:hits.append((fraction,k,hit_x))
                if hits:
                    _,self.room,self.world_x=min(hits)
                    self.x=self.world_x-geometry[self.room][0]
                    self.world_y=ground(geometry[self.room],self.x,surfaces.get(self.room,"flat"))
                    self.visited.add(self.room);self.falling=False;self.vy=0
                    landed=True;break
            if not landed:
                self.world_x=end_x;self.world_y=end_y
                if self.world_y>bottom+65:self.dead=True;self.running=False
            return
        if self.room not in geometry:return
        r=geometry[self.room];self.waiting=False
        kind=surfaces.get(self.room,"flat")
        self.speed=90*speed(kind,slope(r[2],r[3],self.x,kind))
        next_x=min(r[2]-10,self.x+dt*self.speed)
        world_x=r[0]+next_x
        if blocker and blocker[0]-10<=world_x<=blocker[0]+blocker[2]+10 and blocker[1]<=ground(r,next_x,kind)<=blocker[1]+blocker[3]:
            self.waiting=True;return
        if self.room=='goal' and not exit_open:
            self.x=min(next_x,r[2]*.42);self.waiting=True;return
        self.x=next_x
        if self.room=='goal' and self.x>=r[2]*.72:
            self.won=True;return
        if self.x>=r[2]-10:
            target=neighbor(self.room,geometry,surfaces)
            if target and (target!='goal' or exit_open):
                self.room=target;self.x=10.;self.visited.add(target)
            elif target:
                self.waiting=True  # A locked door is solid, not a gap.
            else:
                self.world_x=r[0]+r[2]+1
                self.world_y=ground(r,r[2],kind)
                self.vy=0.;self.falling=True;self.room=None

"""Shared rotating walls: artwork and collision use exactly the same segments."""
import math
# Reference symbol, with only the upper entrance cut open. Wider for a lemur.
PATHS=(
 ((128,22),(30,22),(30,188),(128,188),(128,166)),
 ((165,22),(200,22),(200,188),(150,188)),
 ((128,22),(128,44),(52,44),(52,166),(177,166),(177,44),(165,44)),
 ((30,105),(52,105)),
)

def point(x,y,rect,angle):
 ox,oy,w,h=rect;s=min(w/230,h/210);co,si=math.cos(angle),math.sin(angle)
 x=(x-115)*s;y=(y-105)*s
 return ox+w/2+x*co-y*si,oy+h/2+x*si+y*co

def walls(rect,angle):
 return [(point(*a,rect,angle),point(*b,rect,angle)) for path in PATHS for a,b in zip(path,path[1:])]

def resolve(a,ox,oy,dt,rect,angle,previous):
 """Substep a round body against the visible walls, allowing soft catches."""
 cx,cy=rect[0]+rect[2]/2,rect[1]+rect[3]/2
 if math.hypot(ox-cx,oy-12-cy)>max(rect[2:])*.8 and math.hypot(a.x-cx,a.y-12-cy)>max(rect[2:])*.8:return
 x,y=ox,oy-12
 if getattr(a,'caught',False):
  co,si=math.cos(angle-previous),math.sin(angle-previous);dx,dy=x-cx,y-cy
  x,y=cx+dx*co-dy*si,cy+dx*si+dy*co
 vx=-abs(a.speed)*.45 if getattr(a,'caught',False) else a.speed*.4
 vy=a.vy-600*dt;segments=walls(rect,angle);n=max(1,math.ceil(dt*240));h=dt/n
 for _ in range(n):
  vy+=600*h;x+=vx*h;y+=vy*h
  for _ in range(3):
   for (ax,ay),(bx,by) in segments:
    dx,dy=bx-ax,by-ay;u=max(0,min(1,((x-ax)*dx+(y-ay)*dy)/(dx*dx+dy*dy)))
    nx,ny=x-(ax+u*dx),y-(ay+u*dy);d=math.hypot(nx,ny)
    if d<12:
     if d<1e-6:nx,ny,d=-dy,dx,math.hypot(dx,dy)
     nx/=d;ny/=d;x+=nx*(12-d);y+=ny*(12-d)
     inward=vx*nx+vy*ny
     if inward<0:vx-=inward*nx;vy-=inward*ny
     a.caught=True;a.speed=-abs(a.speed)
 a.x,a.y,a.vy=x,y+12,vy
 if getattr(a,'caught',False):
  a.drop=a.y # cushioned contact, including while tumbling inside
  if math.hypot(x-cx,y-cy)>max(rect[2:])*.72:a.caught=False

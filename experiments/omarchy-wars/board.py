"""Desktop windows are rooms: joined edges open routes, gaps are solid walls."""
import math

class Board:
 def __init__(self,rects,invasion=False):self.rects=dict(rects);self.invasion=invasion
 def room(self,x,y):
  return next((name for name,(rx,ry,w,h) in self.rects.items() if rx<=x<=rx+w and ry<=y<=ry+h),None)
 def center(self,name):
  x,y,w,h=self.rects[name];return x+w/2,y+h/2
 def neighbors(self,name):
  x,y,w,h=self.rects[name];result=[]
  for key,(a,b,c,d) in self.rects.items():
   if key==name:continue
   horizontal=min(abs(x+w-a),abs(a+c-x))<=18 and min(y+h,b+d)-max(y,b)>35
   vertical=min(abs(y+h-b),abs(b+d-y))<=18 and min(x+w,a+c)-max(x,a)>35
   overlap=min(x+w,a+c)-max(x,a)>0 and min(y+h,b+d)-max(y,b)>0
   if horizontal or vertical or overlap:result.append(key)
  return result
 def constrain(self,ox,oy,x,y):
  room=self.room(ox,oy)
  if room is None:return ox,oy
  rx,ry,w,h=self.rects[room]
  if self.invasion and room.startswith('attack'):
   return max(rx+w*.28,min(rx+w*.72,x)),max(ry+h*.38,min(ry+h*.62,y))
  if self.invasion:
   margin=min(22,w/4,h/4)
   return max(rx+margin,min(rx+w-margin,x)),max(ry+margin,min(ry+h-margin,y))
  if rx<=x<=rx+w and ry<=y<=ry+h:return x,y
  # Only a directly neighboring window may receive a crossing actor.
  for key in self.neighbors(room):
   a,b,c,d=self.rects[key]
   if a-18<=x<=a+c+18 and b-18<=y<=b+d+18:
    return max(a+.1,min(a+c-.1,x)),max(b+.1,min(b+d-.1,y))
  return max(rx+.1,min(rx+w-.1,x)),max(ry+.1,min(ry+h-.1,y))
 def projectile(self,ox,oy,x,y):
  if self.invasion:return x,y
  # Subdivide fast bullets so they cannot tunnel across disconnected windows.
  count=max(1,math.ceil(math.hypot(x-ox,y-oy)/8));px,py=ox,oy
  for i in range(1,count+1):
   nx=ox+(x-ox)*i/count;ny=oy+(y-oy)*i/count
   tx,ty=self.constrain(px,py,nx,ny)
   if abs(tx-nx)>18 or abs(ty-ny)>18:return None
   if self.room(nx,ny) is None and self.room(tx,ty)==self.room(px,py):return None
   px,py=tx,ty
  return px,py
 def window_hit(self,ox,oy,x,y,nodes):
  sx,sy=getattr(self,'visual_scale',(1,1));angles=getattr(self,'angles',{})
  steps=max(1,math.ceil(math.hypot(x-ox,y-oy)/3))
  for i in range(steps+1):
   px=ox+(x-ox)*i/steps;py=oy+(y-oy)*i/steps
   for role,node in nodes.items():
    if node['hp']<=0 or role not in self.rects:continue
    rx,ry,w,h=self.rects[role];angle=angles.get(role,0)
    dx=(px-rx-w/2)/sx;dy=(py-ry-h/2)/sy
    lx=dx*math.cos(angle)+dy*math.sin(angle);ly=-dx*math.sin(angle)+dy*math.cos(angle)
    if abs(lx)<=w/sx*.39 and abs(ly)<=h/sy*.325:return role
  return None
 def spawn(self,rng):
  name=rng.choice(['breach','scanner']);x,y,w,h=self.rects[name]
  return x+w*.65,y+h*rng.uniform(.25,.75),0 if name=='breach' else 1
 def relocate(self,newrects,game):
  # Carry everything inside a dragged window with that window.
  things=[game]+game.enemies+game.shots+game.sparks+game.pickups
  for item in things:
   room=getattr(item,'room',None) or self.room(item.x,item.y)
   if room and room in newrects:
    old=self.rects[room];new=newrects[room]
    item.x=max(new[0]+.1,min(new[0]+new[2]-.1,item.x+new[0]-old[0]))
    item.y=max(new[1]+.1,min(new[1]+new[3]-.1,item.y+new[1]-old[1]))
  self.rects=dict(newrects)

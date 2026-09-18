"""Deterministic arena simulation. The install sequence is fictional."""
import math,random
from difficulty import settings
from dataclasses import dataclass
W,H=1100,720
INSTALL_DURATION=9.99
WARNING_DURATION=4.5
@dataclass
class Shot:
 x:float;y:float;vx:float;vy:float;enemy:bool=False;life:float=2.
@dataclass
class Pickup:
 x:float;y:float;vx:float;vy:float;age:float=0.;life:float=18.;room:str="home"
@dataclass
class Enemy:
 x:float;y:float;kind:int;hp:int=1;age:float=0.;cool:float=1.
@dataclass
class Spark:
 x:float;y:float;vx:float;vy:float;life:float;color:str;total:float

def hit_segment(ax,ay,bx,by,x,y,r):
 dx,dy=bx-ax,by-ay;t=max(0,min(1,((x-ax)*dx+(y-ay)*dy)/max(.001,dx*dx+dy*dy)))
 return (ax+t*dx-x)**2+(ay+t*dy-y)**2<=r*r

class Game:
 def __init__(self,seed=None,board=None):
  self.board=board
  self.rng=random.Random(seed);self.state='title';self.clock=0.;self.age=0.;self.playtime=0.
  self.x,self.y=board.center('home') if board else (W/2,H/2);self.angle=0.;self.hp=3;self.score=0;self.wave=1
  self.lasers=1;self.pickups=[];self.pickup_due=self.rng.uniform(7,11);self.upgrade_flash=0.
  self.nodes={};self.respawns={};self.destroyed=0
  self.shots=[];self.enemies=[];self.sparks=[];self.fire=0.;self.spawn=1.;self.invuln=0.;self.dash_cool=0.;self.dash_time=0.;self.dash_dir=(1,0);self.shake=0.
 def burst(self,x,y,color,n=24):
  for _ in range(n):
   a=self.rng.random()*math.tau;v=self.rng.uniform(40,260);life=self.rng.uniform(.2,.8)
   self.sparks.append(Spark(x,y,math.cos(a)*v,math.sin(a)*v,life,color,life))
  self.sparks=self.sparks[-650:]
 def damage(self):
  if self.invuln>0:return
  self.hp-=1;self.invuln=1.3;self.shake=12;self.burst(self.x,self.y,'red',40)
  if self.hp<=0:self.state='over';self.age=0.;self.burst(self.x,self.y,'foreground',60)
 def step(self,dt,move=(0,0),aim=None,shoot=False,dash=False):
  dt=min(.04,max(0,dt));self.clock+=dt;self.age+=dt;self.shake=max(0,self.shake-dt*35)
  for p in self.sparks:p.x+=p.vx*dt;p.y+=p.vy*dt;p.life-=dt;p.vx*=1-dt*2;p.vy*=1-dt*2
  self.sparks=[p for p in self.sparks if p.life>0]
  if self.state=='install' and self.age>=INSTALL_DURATION:self.state='record';self.age=0.;self.burst(W/2,H/2,'bright_green',70)
  elif self.state=='record' and self.age>=1.8:self.state='warning';self.age=0.
  elif self.state=='warning' and self.age>=WARNING_DURATION:self.state='play';self.age=0.
  if self.state!='play':return
  self.playtime+=dt;self.wave=1+int(self.playtime/18)
  difficulty=settings(self.playtime)
  self.upgrade_flash=max(0,self.upgrade_flash-dt)
  self.pickup_due-=dt
  rx,ry,rw,rh=self.board.rects['home'] if self.board else (0,70,W,H-100)
  margin=min(32,rw/4,rh/4)
  if self.lasers<4 and not self.pickups and self.pickup_due<=0:
   self.pickups.append(Pickup(self.rng.uniform(rx+margin,rx+rw-margin),self.rng.uniform(ry+margin,ry+rh-margin),self.rng.choice((-1,1))*23,self.rng.choice((-1,1))*17))
   self.pickup_due=self.rng.uniform(13,21)
  for p in self.pickups:
   p.age+=dt;p.life-=dt;p.x+=p.vx*dt;p.y+=p.vy*dt
   if p.x<rx+margin or p.x>rx+rw-margin:p.vx=-p.vx;p.x=max(rx+margin,min(rx+rw-margin,p.x))
   if p.y<ry+margin or p.y>ry+rh-margin:p.vy=-p.vy;p.y=max(ry+margin,min(ry+rh-margin,p.y))
  self.fire-=dt;self.invuln=max(0,self.invuln-dt);self.dash_cool=max(0,self.dash_cool-dt);self.dash_time=max(0,self.dash_time-dt)
  if aim:self.angle=math.atan2(aim[1]-self.y,aim[0]-self.x)
  mx,my=move;length=math.hypot(mx,my)
  if length:mx/=length;my/=length
  if dash and self.dash_cool<=0:
   self.dash_time=.16;self.dash_cool=1.5;self.invuln=max(self.invuln,.22);self.dash_dir=(mx,my) if length else (math.cos(self.angle),math.sin(self.angle));self.burst(self.x,self.y,'cyan',12)
  speed=290
  if self.dash_time>0:mx,my=self.dash_dir;speed=850
  if self.board:self.x,self.y=self.board.constrain(self.x,self.y,self.x+mx*speed*dt,self.y+my*speed*dt)
  else:self.x=max(30,min(W-30,self.x+mx*speed*dt));self.y=max(95,min(H-55,self.y+my*speed*dt))
  for p in self.pickups:
   if p.life>0 and math.hypot(p.x-self.x,p.y-self.y)<20:
    self.lasers=min(4,self.lasers+1);p.life=0;self.upgrade_flash=2.5;self.burst(p.x,p.y,'bright_green',40)
  self.pickups=[p for p in self.pickups if p.life>0 and self.lasers<4]
  if shoot and self.fire<=0:
   self.fire=.085;dx,dy=math.cos(self.angle),math.sin(self.angle)
   for i in range(self.lasers):
    offset=(i-(self.lasers-1)/2)*6
    self.shots.append(Shot(self.x-dy*offset,self.y+dx*offset,dx*850,dy*850))
  self.spawn-=dt
  if self.spawn<=0 and len(self.enemies)<65:
   self.spawn=max(.18,1.05-self.wave*.08)
   side=self.rng.randrange(4);x=self.rng.uniform(25,W-25);y=self.rng.uniform(90,H-55)
   if side==0:x=20
   elif side==1:x=W-20
   elif side==2:y=85
   else:y=H-45
   kind=self.rng.randrange(min(3,self.wave))
   if self.board:x,y,kind=self.board.spawn(self.rng)
   self.enemies.append(Enemy(x,y,kind,2 if kind==2 else 1))
  if self.board and self.board.invasion:
   for role,node in self.nodes.items():
    node['cool']-=dt
    if node['hp']>0 and node['cool']<=0 and len(self.enemies)<difficulty['cap']:
     node['cool']=self.rng.uniform(difficulty['reinforce_low'],difficulty['reinforce_high']);x,y=self.board.center(role)
     e=Enemy(x,y,int(role[6:])%3,cool=2.);e.room=role;self.enemies.append(e)
  for e in self.enemies:
   e.age+=dt;e.cool-=dt
   if e.age<.65:continue
   angle=math.atan2(self.y-e.y,self.x-e.x);distance=math.hypot(self.x-e.x,self.y-e.y)
   speed=85+self.wave*6 if e.kind==0 else 65 if e.kind==1 else 120
   if self.board and self.board.invasion:speed*=difficulty['speed']
   if e.kind==1 and distance<260 and not (self.board and self.board.invasion):speed=-25
   if e.kind==2:angle+=math.sin(e.age*7)*.65
   ex,ey=e.x,e.y;e.x+=math.cos(angle)*speed*dt;e.y+=math.sin(angle)*speed*dt
   if self.board and not self.board.invasion:e.x,e.y=self.board.constrain(ex,ey,e.x,e.y)
   elif self.board:
    e.x=max(8,min(W-8,e.x));e.y=max(8,min(H-8,e.y));e.room=None
   if (e.kind==1 or self.board and self.board.invasion) and e.cool<=0 and len(self.shots)<220 and (not self.board or not self.board.invasion or difficulty['can_shoot']):
    e.cool=difficulty['fire_interval'] if self.board and self.board.invasion else 1.6
    bullet_speed=difficulty['bullet_speed'] if self.board and self.board.invasion else 230
    self.shots.append(Shot(e.x,e.y,math.cos(angle)*bullet_speed,math.sin(angle)*bullet_speed,True,6))
   e.phasing=bool(self.board and self.board.invasion and self.board.room(e.x,e.y)!='home' and self.board.window_hit(e.x,e.y,e.x,e.y,self.nodes) is None)
   connected=True
   if self.board and not self.board.invasion:
    enemy_room=self.board.room(e.x,e.y);ship_room=self.board.room(self.x,self.y)
    connected=enemy_room is not None and (enemy_room==ship_room or ship_room in self.board.neighbors(enemy_room))
   if distance<15 and connected:self.damage()
  for b in self.shots:
   ox,oy=b.x,b.y;b.x+=b.vx*dt;b.y+=b.vy*dt;b.life-=dt
   if self.board:
    result=self.board.projectile(ox,oy,b.x,b.y)
    if result is None:b.life=0;continue
    b.x,b.y=result
   if b.enemy:
    if hit_segment(ox,oy,b.x,b.y,self.x,self.y,9):self.damage();b.life=0
   else:
    for e in self.enemies:
     if e.hp>0 and e.age>.65 and hit_segment(ox,oy,b.x,b.y,e.x,e.y,10):
      e.hp-=1;b.life=0;self.burst(e.x,e.y,('red','orange','blue')[e.kind],24 if e.hp<=0 else 6)
      if e.hp<=0:self.score+=100*(e.kind+1);self.shake=max(self.shake,3)
      break
   if not b.enemy and b.life>0 and self.board and self.board.invasion:
    role=self.board.window_hit(ox,oy,b.x,b.y,self.nodes)
    if role:
     node=self.nodes[role];node['hp']-=1;b.life=0
     x,y=self.board.center(role);self.burst(x,y,'orange',5)
     if node['hp']<=0:
      self.score+=1000;self.destroyed+=1;self.shake=9;self.burst(x,y,'red',70)
      self.respawns[role]=self.playtime+self.rng.uniform(difficulty['respawn_low'],difficulty['respawn_high'])
  self.enemies=[e for e in self.enemies if e.hp>0]
  self.shots=[b for b in self.shots if b.life>0 and (0<b.x<W and 0<b.y<H if self.board and self.board.invasion else self.board.room(b.x,b.y) is not None if self.board else 0<b.x<W and 70<b.y<H-30)]

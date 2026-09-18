"""Short mechanical press, latch rebound, and cartridge seating motion."""
import math
DURATION=.85

def seat_rect(console,cartridge):
 x,y,w,h=console;_,_,cw,ch=cartridge
 return (round(x+w/2-cw/2),round(y+h*.32-ch),cw,ch)

def travel(age):
 if age<0:return 0.
 if age<.12:return 24*(1-(1-age/.12)**3)
 if age<.24:return 24-7*math.sin((age-.12)/.12*math.pi/2)
 u=min(1,(age-.24)/.38)
 return 17+153*(u*u*(3-2*u))

def kick(age):
 return 3*math.sin(age*55)*math.exp(-age*10) if 0<=age<.6 else 0.

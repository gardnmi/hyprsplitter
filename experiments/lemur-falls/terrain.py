"""Shared Windows hill silhouette, collision height and chair slope."""
import math

def hill_y(x,w,h):
 floor=h-20;u=max(0,min(1,x/max(1,w-112)))
 return floor-(h-20)*(.47*math.sin(math.pi*u)**2+.055*math.sin(3*math.pi*u)**2)

def ground(x,rect):
 ox,oy,w,h=rect
 return oy+hill_y(x-ox,w,h)

def slope(x,rect):return (ground(x+2,rect)-ground(x-2,rect))/4

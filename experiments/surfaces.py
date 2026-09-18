"""One surface definition shared by collision and drawing."""
import math


def height(w,h,x,kind='flat'):
    base=h-34
    if kind=='hill':
        amplitude=max(0,min(130,(h-150)*.5,w*.27))
        u=max(0,min(1,x/max(1,w)))
        return base-amplitude*math.sin(math.pi*u)**2
    return base


def slope(w,h,x,kind='flat'):
    return (height(w,h,x+1,kind)-height(w,h,x-1,kind))/2


def speed(kind,gradient=0):
    if kind=='water':return .65
    if kind=='mud':return .42
    if kind=='fast':return 1.8
    if kind=='hill':return max(.6,min(1.25,1+gradient*.3))/math.sqrt(1+gradient*gradient)
    return 1.

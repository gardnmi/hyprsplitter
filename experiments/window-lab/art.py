"""Small Cairo illustrations for the window interaction playground."""
import math
import cairo

BLUE = (.40, .78, 1)
GOLD = (1, .80, .36)
GREEN = (.4, .9, .6)
WHITE = (.83, .91, .96)


def line(c, points, color=WHITE, width=4):
    c.set_source_rgb(*color); c.set_line_width(width)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.move_to(*points[0])
    for p in points[1:]: c.line_to(*p)
    c.stroke()


def circle(c, x, y, r, color=WHITE):
    c.set_source_rgb(*color); c.arc(x,y,r,0,math.tau); c.fill()


def box(c,x,y,w,h,color):
    c.set_source_rgb(*color); c.rectangle(x,y,w,h); c.fill()


def label(c, value, x, y, size=14, color=WHITE):
    c.set_source_rgb(*color); c.select_font_face('sans-serif',0,0)
    c.set_font_size(size); c.move_to(x,y); c.show_text(value)


def walker(c,x,y,bounce=0):
    y-=bounce
    circle(c,x,y-52,9,GOLD)
    for p in [[(x,y-40),(x,y-20)],[(x-13,y-24),(x,y-37),(x+13,y-24)],[(x-13,y),(x,y-20),(x+13,y)]]:
        line(c,p,GOLD,4)


def icon(c, kind, p, active, t):
    """Draw in a 300 by 190 design canvas."""
    c.new_path()
    if kind == 'cloud':
        for i in range(20):
            x=95+110*((i*.618)%1); y=95+(t*115+i*31)%86
            line(c,[(x,y),(x-2,y+8)],BLUE,2)
        for x,y,r in [(105,70,25),(135,54,33),(172,59,36),(200,76,25),(152,80,30)]:circle(c,x,y,r)
        circle(c,137,73,2,(.1,.2,.3));circle(c,165,73,2,(.1,.2,.3))
        c.set_source_rgb(.1,.2,.3);c.set_line_width(2);c.arc(151,79,7,.2,math.pi-.2);c.stroke()
    elif kind == 'fire':
        line(c,[(78,160),(225,170)],(.35,.22,.13),12)
        for i in range(9):
            x=90+i*15; height=(72+20*math.sin(t*7+i*2))*(1-p)
            if height<1:continue
            for scale,color in [(1,(1,.26,.07)),(.55,GOLD)]:
                c.set_source_rgb(*color);c.move_to(x-13*scale,158)
                c.curve_to(x-28*scale,120,x+12,158-height*scale,x,158-height*scale)
                c.curve_to(x+5,140,x+24*scale,152,x+13*scale,158);c.fill()
        if active:
            for i in range(16):
                x=90+i*8;y=20+(t*115+i*31)%133
                line(c,[(x,y),(x-2,y+8)],BLUE,2)
    elif kind == 'sun':
        for i in range(12):
            a=i*math.tau/12+t*.15
            line(c,[(150+48*math.cos(a),85+48*math.sin(a)),(150+65*math.cos(a),85+65*math.sin(a))],GOLD,5)
        circle(c,150,85,35,GOLD)
    elif kind == 'ice':
        box(c,98,160-115*(1-p),104,115*(1-p),(.37,.72,.90))
        line(c,[(75,170),(225,170)],BLUE,4+8*p)
        key(c,150,125 if p<1 else 152)
    elif kind == 'fan':
        line(c,[(150,95),(150,161)],WHITE,7);line(c,[(122,165),(178,165)],WHITE,7)
        for i in range(3):
            a=t*8+i*math.tau/3
            line(c,[(150,85),(150+40*math.cos(a),85+40*math.sin(a))],BLUE,17)
        circle(c,150,85,10)
        for i in range(4):
            x=205+(t*100+i*23)%80
            line(c,[(x,50+i*23),(x+16,50+i*23)],BLUE,2)
    elif kind == 'boat':
        x=55+p*180
        line(c,[(0,161),(300,161)],BLUE,3)
        c.set_source_rgb(.55,.34,.2);c.move_to(x-33,130);c.line_to(x+33,130);c.line_to(x+20,150);c.line_to(x-20,150);c.close_path();c.fill()
        line(c,[(x,132),(x,65)],WHITE,3)
        c.set_source_rgb(*GOLD);c.move_to(x+4,70);c.line_to(x+33,123);c.line_to(x+4,123);c.fill()
    elif kind == 'magnet':
        c.set_source_rgb(.95,.3,.32);c.set_line_width(23);c.arc(150,90,40,0,math.pi);c.stroke()
        line(c,[(110,90),(110,50)],(.95,.3,.32),23);line(c,[(190,90),(190,50)],(.95,.3,.32),23)
        box(c,98,42,24,20,WHITE);box(c,178,42,24,20,WHITE)
    elif kind == 'key':
        line(c,[(20,162),(85,162)],(.35,.45,.5));line(c,[(215,162),(280,162)],(.35,.45,.5))
        key(c,150-95*p,100-30*p)
    elif kind == 'plant':
        box(c,80,155,140,15,(.35,.22,.13))
        line(c,[(150,155),(150,145-115*p)],GREEN,5)
        for i in range(int(p*7)):
            y=142-i*15;sign=1 if i%2 else -1
            line(c,[(150,y),(150+25*sign,y-13)],GREEN,9)
        if p>=1:circle(c,150,28,13,GOLD)
        elif p==0:circle(c,150,150,6,GOLD)
    elif kind == 'battery':
        box(c,95,52,105,80,WHITE);box(c,200,76,10,30,WHITE)
        box(c,102,59,91,66,(.06,.13,.16));box(c,109,65,76,54,GREEN)
        label(c,'+',143,106,30,(.07,.22,.13))
    elif kind == 'robot':
        box(c,112,55,76,63,(.40,.54,.65));box(c,107,123,86,30,(.28,.4,.5))
        for x in (132,169):circle(c,x,80,7,GREEN if p>=1 else (.15,.23,.3))
        line(c,[(150,55),(150,35)],WHITE,3);circle(c,150,29,5,GOLD)
        box(c,121,101,58*p,5,GREEN)
        for x in (122,178):line(c,[(x,153),(x,170+math.sin(t*7)*5 if p>=1 else 170)],WHITE,6)
    elif kind == 'shield':
        c.set_source_rgb(.2,.52,.74);c.move_to(105,40);c.line_to(195,40);c.line_to(190,115);c.line_to(150,155);c.line_to(110,115);c.close_path();c.fill()
        line(c,[(150,55),(150,130)],BLUE,5)
        if active:circle(c,102,80,12+math.sin(t*20)*4,GOLD)
    elif kind == 'walker':
        walker(c,210,165)
        if int(t*3)%3==0:
            line(c,[(0,113),(125 if active else 197,113)],(1,.28,.23),4)
        if active:line(c,[(130,72),(130,155)],BLUE,6)
        for i in range(3):circle(c,120+i*27,32,6,GREEN if p>=(i+1)/3 else (.2,.3,.35))
    elif kind == 'trampoline':
        line(c,[(75,130),(225,130)],(.7,.4,.95),9)
        for x in (90,210):line(c,[(x,135),(x-8,145),(x+8,153),(x,165)],WHITE,3)
        line(c,[(150,98),(150,39)],BLUE,3);line(c,[(135,55),(150,39),(165,55)],BLUE,3)
    elif kind == 'jumper':
        line(c,[(0,170),(100,170)],WHITE);line(c,[(205,55),(300,55)],GREEN)
        x=80+150*p; y=170-115*p
        walker(c,x,y,math.sin(p*math.pi)*80)
    elif kind == 'weight':
        circle(c,150,57,23,WHITE);circle(c,150,57,15,(.05,.1,.16))
        c.set_source_rgb(.4,.48,.55);c.move_to(111,65);c.line_to(189,65);c.line_to(212,150);c.line_to(88,150);c.close_path();c.fill()
        label(c,'10',130,124,29)
    elif kind == 'bridge':
        line(c,[(0,165),(85,165)],WHITE,8);line(c,[(220,165),(300,165)],WHITE,8)
        a=(1-p)*math.pi/2
        line(c,[(85,160),(85+135*math.cos(a),160-135*math.sin(a))],GOLD,9)
        line(c,[(105,180),(200,180)],BLUE,3)
    elif kind == 'lantern':
        c.set_source_rgba(1,.78,.3,.10);c.arc(150,100,77,0,math.tau);c.fill()
        circle(c,150,100,31,GOLD)
        line(c,[(112,143),(112,59),(188,59),(188,143),(112,143)],WHITE,5)
        line(c,[(133,59),(133,33),(167,33),(167,59)],WHITE,4)
    elif kind == 'ghost':
        alpha=.12+.88*p
        if p>=1:alpha=.35+.2*math.sin(t*3)
        c.set_source_rgba(.8,.9,1,alpha)
        x=150+(p*55 if p>=1 else 0);y=82+math.sin(t*2)*7
        c.arc(x,y,36,math.pi,math.tau);c.line_to(x+36,y+65)
        for i in range(6):c.line_to(x+36-i*14,y+55+(i%2)*13)
        c.close_path();c.fill()
        circle(c,x-12,y+9,5,(.07,.12,.2));circle(c,x+12,y+9,5,(.07,.12,.2))


def key(c,x,y):
    c.set_source_rgb(*GOLD);c.set_line_width(5);c.arc(x-20,y,12,0,math.tau);c.stroke()
    line(c,[(x-8,y),(x+25,y),(x+25,y+10)],GOLD,5)
    line(c,[(x+13,y),(x+13,y+8)],GOLD,5)

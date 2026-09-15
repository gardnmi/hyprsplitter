"""Procedural vector artwork for the native lesson windows."""

import math
import random
from controls import MISSIONS
from field import COLUMNS, SECTORS, sector

BG = (0.025, 0.043, 0.075)
CYAN = (0.3, 0.94, 0.86)
WHITE = (0.87, 0.93, 1)
MUTED = (0.37, 0.48, 0.62)
RED = (1, 0.28, 0.35)
AMBER = (1, 0.70, 0.29)
STARS = [(random.Random(i).random(), random.Random(i + 500).random(), 0.5 + i % 3 * .4) for i in range(48)]


def color(cr, rgb, alpha=1):
    cr.set_source_rgba(*rgb, alpha)


def text(cr, message, x, y, size=14, tint=WHITE, center=False):
    cr.select_font_face("monospace", 0, 0)
    cr.set_font_size(size)
    color(cr, tint)
    if center:
        ext = cr.text_extents(message)
        x -= ext.width / 2 + ext.x_bearing
    cr.move_to(x, y)
    cr.show_text(message)


def line(cr, points, tint, width=1, alpha=1, fill=False):
    color(cr, tint, alpha)
    cr.set_line_width(width)
    cr.move_to(*points[0])
    for point in points[1:]:
        cr.line_to(*point)
    if fill:
        cr.close_path()
        cr.fill()
    else:
        cr.stroke()


def ship(cr, x, y, t):
    cr.save()
    cr.translate(x, y)
    color(cr, CYAN, .09)
    cr.arc(0, 0, 66, 0, math.tau)
    cr.fill()
    cr.set_line_width(1)
    color(cr, CYAN, .35)
    cr.arc(0, 0, 65, t * .2, t * .2 + math.pi * 1.55)
    cr.stroke()
    flame = 40 + math.sin(t * 19) * 9
    line(cr, [(-10, 29), (0, flame + 13), (10, 29)], AMBER, fill=True)
    line(cr, [(-4, 29), (0, flame), (4, 29)], WHITE, fill=True)
    hull = [(0, -46), (16, -7), (40, 25), (14, 19), (9, 33), (-9, 33), (-14, 19), (-40, 25), (-16, -7), (0, -46)]
    line(cr, hull, (0.10, .25, .30), fill=True)
    line(cr, hull, CYAN, 2)
    line(cr, [(0, -27), (7, -5), (0, 5), (-7, -5)], WHITE, fill=True)
    line(cr, [(0, 9), (0, 25)], CYAN, 2)
    cr.restore()


def enemy(cr, x, y, tint):
    line(cr, [(x-25, y-10), (x-13, y+12), (x, y+5), (x+13, y+12), (x+25, y-10), (x+9, y-4), (x, y-15), (x-9, y-4), (x-25, y-10)], tint, 2)


def asteroid(cr, x, y, radius, t, alpha=1):
    points = [(x + math.cos(i * math.tau / 9 + t*.15) * radius * (1 if i % 2 else .78),
               y + math.sin(i * math.tau / 9 + t*.15) * radius * (1 if i % 2 else .78)) for i in range(9)]
    points.append(points[0])
    line(cr, points, AMBER, 2, alpha)
    color(cr, AMBER, alpha * .3)
    cr.arc(x-radius*.2, y-radius*.15, radius*.17, 0, math.tau)
    cr.stroke()


def fitted(cr, message, x, y, width, size=15, tint=WHITE):
    cr.select_font_face('monospace', 0, 0)
    cr.set_font_size(size)
    extent = cr.text_extents(message).width
    text(cr, message, x, y, min(size, size*width/max(1,extent)), tint, True)


def draw_tile(cr, w, h, game, actor, ready, away, t):
    color(cr, BG); cr.paint()
    scale = min(w/480, h/320, 1.5)
    cr.scale(scale,scale)
    w,h = w/scale,h/scale
    for sx,sy,radius in STARS:
        color(cr,MUTED,.35)
        cr.arc(sx*w,(sy*h+t*2)%h,radius,0,math.tau);cr.fill()
    mission = MISSIONS[game.index]
    pilot = actor == 4
    selected = actor == game.focused
    rect = game.geometry.get(actor)
    slot = actor
    if rect:
        slot = sector(rect, game.arena)
    danger = False
    if game.mission == 'asteroids' and game.state == 'active':
        danger = slot in game.rocks or slot in game.flashes
        if danger:
            color(cr,AMBER,.25 if slot in game.flashes else .09);cr.paint()
            asteroid(cr,w/2,h/2-20,50,t)
            fitted(cr, f'IMPACT IN {game.rocks[slot]:.1f}s' if slot in game.rocks else 'IMPACT',w/2,77,w-40,16,AMBER)
        elif not pilot:
            fitted(cr,'EXPLORED' if slot in game.visited else 'UNVISITED / FLY HERE',w/2,h/2,w-50,17,MUTED if slot in game.visited else CYAN)
    elif game.mission == 'lasers' and game.state == 'active' and rect:
        # Draw the actual unsafe half in desktop coordinates; it stays in place
        # while the user's two real windows rotate or swap around it.
        x,y,aw,ah = game.arena
        safe = game.fired_side if game.cooldown else game.safe_side
        dx,dy,dw,dh = {'top':(x,y+ah/2,aw,ah/2),'bottom':(x,y,aw,ah/2),
                       'left':(x+aw/2,y,aw/2,ah),'right':(x,y,aw/2,ah)}[safe]
        rx,ry = rect['at']
        rw,rh = rect['size']
        color(cr,RED,.10)
        cr.rectangle((dx-rx)/rw*w,(dy-ry)/rh*h,dw/rw*w,dh/rh*h);cr.fill()
        cr.save()
        cr.rectangle((dx-rx)/rw*w,(dy-ry)/rh*h,dw/rw*w,dh/rh*h);cr.clip()
        horizontal = safe in ('top','bottom')
        for offset in (.2,.5,.8):
            points = ([(0,(dy+dh*offset-ry)/rh*h),(w,(dy+dh*offset-ry)/rh*h)] if horizontal
                      else [((dx+dw*offset-rx)/rw*w,0),((dx+dw*offset-rx)/rw*w,h)])
            if game.cooldown:
                line(cr,points,RED,24,.2)
                line(cr,points,WHITE,3,.8)
            else:
                cr.set_dash([6,12]);line(cr,points,RED,1,.35);cr.set_dash([])
        cr.restore()
        from game import side
        danger = side(rect,game.arena) != safe
        fitted(cr, f'SAFE HALF: {safe.upper()} / LASER IN {game.timer:.1f}s' if not game.cooldown else game.feedback,
               w/2,77,w-40,16,RED if danger else CYAN)
        # A compact map makes the world-space safe half unambiguous.
        mx,my,mw,mh = 28,92,96,56
        color(cr,RED,.4);cr.rectangle(mx,my,mw,mh);cr.fill()
        sx,sy,sw,sh = {'top':(0,0,1,.5),'bottom':(0,.5,1,.5),'left':(0,0,.5,1),'right':(.5,0,.5,1)}[safe]
        color(cr,CYAN,.85);cr.rectangle(mx+sx*mw,my+sy*mh,sw*mw,sh*mh);cr.fill()
    elif game.mission == 'float' and not pilot and rect:
        bx,by = game.beacon
        rx,ry = rect['at'];rw,rh = rect['size']
        bx,by = (bx-rx)/rw*w,(by-ry)/rh*h
        color(cr,CYAN,.7);cr.set_line_width(2)
        cr.arc(bx,by,42,0,math.tau);cr.stroke()
        line(cr,[(bx-55,by),(bx+55,by)],CYAN,1,.5)
        line(cr,[(bx,by-55),(bx,by+55)],CYAN,1,.5)
        fitted(cr,'DOCKING BEACON',bx,by+70,min(300,w-40),18,CYAN)

    heading = 'YOUR SHIP' if pilot else 'ENEMY SHIP' if actor in game.enemies else 'SECTOR '+str(slot+1) if game.mission == 'asteroids' else 'SPACE STATION'
    text(cr,heading,20,29,13,CYAN if pilot else RED if actor in game.enemies else MUTED)
    fitted(cr,f'LESSON {game.index+1} / 7',w-92,29,145,12,MUTED)
    line(cr,[(20,43),(w-20,43)],MUTED,1,.3)
    if selected:
        color(cr,CYAN if actor not in game.enemies else AMBER,.8)
        cr.set_line_width(3);cr.rectangle(4,4,w-8,h-8);cr.stroke()
    if pilot:
        ship(cr,w/2,h/2-12,t)
        if game.mission == 'asteroids':
            # Mini chart records travel, without adding a second action.
            for s in range(SECTORS):
                color(cr,CYAN if s in game.visited else MUTED,.7 if s in game.visited else .25)
                cr.rectangle(22+(s%COLUMNS)*9,60+(s//COLUMNS)*9,6,6);cr.fill()
        if game.mission == 'resize' and game.baseline_width:
            target = 1.2 if game.step == 0 else 1
            ratio = rect['size'][0]/game.baseline_width if rect else 1
            barw = min(w-80,360)
            color(cr,MUTED,.3);cr.rectangle(w/2-barw/2,83,barw,6);cr.fill()
            color(cr,CYAN,.8);cr.rectangle(w/2-barw/2,83,barw*min(1,ratio/1.5),6);cr.fill()
            bx = w/2-barw/2+barw*target/1.5
            line(cr,[(bx,77),(bx,96)],AMBER,3)
            fitted(cr,f'TARGET {target:.0%} / CURRENT {ratio:.0%}',w/2,115,w-50,15,CYAN)
        fitted(cr,game.status(),w/2,h-91,w-40,14,CYAN)
    elif actor in game.enemies:
        color(cr,RED,.07);cr.paint()
        cr.save();cr.translate(w/2,h/2-20);cr.scale(2.5,2.5);enemy(cr,0,0,RED);cr.restore()
        fitted(cr,'TARGET SELECTED' if selected else 'SELECT THIS SHIP',w/2,h/2+52,w-40,18,AMBER if selected else RED)
    elif game.mission not in ('asteroids','lasers','float'):
        fitted(cr,'TRAINING STATION',w/2,h/2,w-40,20,MUTED)

    show_card = pilot and (not ready or game.state != 'active' or away or game.paused)
    if show_card:
        color(cr,BG,.97);cr.rectangle(12,52,w-24,h-114);cr.fill()
        if not ready:
            title, detail, key, note = 'PREPARING LESSON', 'Arranging your windows...', '', ''
        elif game.state == 'complete':
            title = 'LESSON COMPLETE' if game.index < 6 else 'FLIGHT SCHOOL COMPLETE'
            detail = mission[1]
            key = 'SPACE / NEXT LESSON' if game.index < 6 else '1-7 / REVISIT A LESSON'
            note = 'R to practice again'
        elif away or game.paused:
            title,detail,key,note = 'PAUSED', 'Take your time.', 'SPACE / RESUME' if game.paused else 'RETURN TO THE LESSON', ''
        else:
            title,detail,key,note = mission[1],mission[2],mission[3].format(**game.controls),mission[4]
        fitted(cr,title,w/2,h/2-64,w-40,23,CYAN)
        fitted(cr,detail,w/2,h/2-26,w-40,15)
        fitted(cr,key,w/2,h/2+12,w-40,17,CYAN)
        fitted(cr,note,w/2,h/2+43,w-40,13,MUTED)
        if ready and game.state == 'briefing':
            fitted(cr,'SPACE / START',w/2,h/2+74,w-40,16,CYAN)
    if ready:
        if game.feedback_time and (pilot or actor in game.enemies):
            fitted(cr,game.feedback,w/2,h-68,w-40,12,AMBER)
        if game.state == 'active' and (pilot or selected or actor in game.enemies):
            fitted(cr,game.instruction() if selected or pilot else f"{game.controls['focus']} / SELECT A RED SHIP",w/2,h-43,w-36,16,CYAN)
    if pilot or selected:
        fitted(cr,'SPACE pause   R retry   1-7 lessons   ESC quit',w/2,h-17,w-32,10,MUTED)

"""Procedural vector artwork for the nine native game windows."""

import math
import random

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
               y + math.sin(i * math.tau / 9 + t*.15) * radius * (1 if i % 2 else .78)) for i in range(10)]
    line(cr, points, AMBER, 2, alpha)
    color(cr, AMBER, alpha * .3)
    cr.arc(x-radius*.2, y-radius*.15, radius*.17, 0, math.tau)
    cr.stroke()


def draw_tile(cr, w, h, game, slot, player, ready, away, t):
    color(cr, BG)
    cr.paint()
    # Scale the interface down gracefully on smaller displays.
    scale = min(w / 440, h / 290, 1.35)
    cr.scale(scale, scale)
    w, h = w / scale, h / scale
    for sx, sy, radius in STARS:
        color(cr, MUTED, .3 + radius * .15)
        cr.arc(sx * w, (sy * h + t * (2 + radius)) % h, radius, 0, math.tau)
        cr.fill()
    color(cr, MUTED, .08)
    cr.set_line_width(1)
    for x in range(0, int(w), 48):
        cr.move_to(x, 0)
        cr.line_to(x, h)
    for y in range(0, int(h), 48):
        cr.move_to(0, y)
        cr.line_to(w, y)
    cr.stroke()

    danger = slot in game.hazards and game.phase in ("warning", "impact")
    tint = AMBER if game.kind == "asteroid" else RED
    if danger:
        color(cr, tint, .14 if game.phase == "warning" else .42)
        cr.paint()
        color(cr, tint, .65 + .25 * math.sin(t*8))
        cr.set_line_width(3)
        cr.rectangle(6, 6, w-12, h-12)
        cr.stroke()
        if game.kind == "laser":
            vertical = game.axis == "column"
            if game.phase == "warning":
                cr.set_dash([9, 9], t * 15)
                line(cr, [(w/2, 55), (w/2, h-45)] if vertical else [(0, h/2), (w, h/2)], tint, 2, .55)
                cr.set_dash([])
                enemy(cr, w/2, 70, tint)
            else:
                for width, alpha in [(65, .12), (28, .5), (7, 1)]:
                    line(cr, [(w/2, 0), (w/2, h)] if vertical else [(0, h/2), (w, h/2)], WHITE if width == 7 else tint, width, alpha)
        else:
            asteroid(cr, w/2, h/2, 62 if game.phase == "impact" else 37 + 6*math.sin(t*4), t)

    text(cr, "HYPRSPLITTER" if slot == 0 else f"SECTOR {slot//3+1}.{slot%3+1}", 20, 29, 13, CYAN if slot == 0 else MUTED)
    text(cr, f"{game.score:06d}  /  WAVE {game.wave:02d}", w-230, 29, 13, WHITE)
    line(cr, [(20, 43), (w-20, 43)], MUTED, 1, .25)

    if player:
        if game.hit and game.phase == "impact":
            color(cr, RED, .2)
            cr.paint()
        ship(cr, w/2, h/2-7, t)
        text(cr, "YOU / PILOT 01", w/2, h/2+82, 14, CYAN, True)
        for i in range(3):
            color(cr, CYAN if i < game.shields else MUTED, 1 if i < game.shields else .25)
            cr.rectangle(w/2-39+i*28, h/2+94, 22, 5)
            cr.fill()
    elif not danger:
        text(cr, "CLEAR", w/2, h/2+5, 17, MUTED, True)
        if slot % 3 == 2:
            enemy(cr, w/2, h/2-38, MUTED)

    if not ready or game.phase == "ready" or game.phase == "over" or game.paused or away:
        if slot == 0 or (player and game.phase != "ready"):
            color(cr, BG, .92)
            cr.rectangle(16, h/2-70, w-32, 145)
            cr.fill()
            if not ready:
                title, subtitle = "ASSEMBLING SECTORS", "Building nine real Hyprland tiles"
            elif game.phase == "over":
                title, subtitle = "SHIP LOST", f"SCORE {game.score:06d} / R to restart"
            elif away or game.paused:
                title, subtitle = "PAUSED", "Return to board / Space to resume" if away else "Space to resume"
            else:
                title, subtitle = "MOVE THE WINDOW.", "DODGE THE RED SECTORS."
            text(cr, title, w/2, h/2-26, 22, CYAN, True)
            text(cr, subtitle, w/2, h/2+3, 13, WHITE, True)
            if ready and game.phase == "ready":
                text(cr, "Arrows / WASD to swap your ship", w/2, h/2+30, 12, MUTED, True)
                text(cr, "SPACE TO LAUNCH", w/2, h/2+58, 15, CYAN, True)
    elif danger:
        label = ("ASTEROID INBOUND" if game.kind == "asteroid" else "LASER LOCK") if game.phase == "warning" else "IMPACT"
        text(cr, label, w/2, h-57, 15, tint, True)

    if game.phase == "warning":
        color(cr, tint if danger else CYAN, .8)
        cr.rectangle(20, h-38, (w-40)*max(0, game.remaining/game.duration), 3)
        cr.fill()
    text(cr, "ARROWS / WASD  move    SPACE  pause    R  restart    ESC  quit", w/2, h-15, 10, MUTED, True)

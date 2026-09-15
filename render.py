"""Procedural vector artwork for the nine native game windows."""

import math
import random
from controls import lesson_for

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


def draw_tile(cr, w, h, game, slot, player, ready, away, t, actor=None, controlled=4):
    actor = slot if actor is None else actor
    wing = actor == 9
    player = player or wing
    lesson = lesson_for(max(1, game.wave))
    hints = game.controls
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

    asteroid_impact = slot in game.asteroid_flashes
    danger = (slot in game.hazards and game.phase in ("warning", "impact")) or asteroid_impact
    impact = asteroid_impact if game.kind == "asteroid" else game.phase == "impact"
    tint = AMBER if game.kind == "asteroid" else RED
    if danger:
        color(cr, tint, .42 if impact else .14)
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
            else:
                for width, alpha in [(65, .12), (28, .5), (7, 1)]:
                    line(cr, [(w/2, 0), (w/2, h)] if vertical else [(0, h/2), (w, h/2)], WHITE if width == 7 else tint, width, alpha)
        else:
            progress = 1 - game.asteroid_timers.get(slot, 0) / game.asteroid_delays.get(slot, 1)
            asteroid(cr, w/2, h/2-25*(1-progress), 62 if impact else 20 + progress*32, t + slot)

    label = "HYPRSPLITTER" if actor == 0 else f"SECTOR {slot//3+1}.{slot%3+1}"
    text(cr, label, 20, 29, 13, CYAN if actor == 0 else MUTED)
    text(cr, f"{game.score:06d}  /  WAVE {game.wave:02d}", w-230, 29, 13, WHITE)
    line(cr, [(20, 43), (w-20, 43)], MUTED, 1, .25)

    if player:
        if game.enemies:
            cr.set_dash([5, 6])
            line(cr, [(w/2, h/2-66), (w/2, 47)], CYAN, 2, .55)
            cr.set_dash([])
            line(cr, [(w/2-6, 56), (w/2, 47), (w/2+6, 56)], CYAN, 2)
        if game.contact_flash or (game.hit and game.phase == "impact") or (asteroid_impact and slot in game.asteroid_hits):
            color(cr, RED, .2)
            cr.paint()
        cr.save()
        cr.translate(w/2, h/2-20)
        cr.rotate({"up": 0, "right": math.pi/2, "down": math.pi, "left": -math.pi/2}[game.shot_direction])
        ship(cr, 0, 0, t)
        cr.restore()
        name = "WING" if wing else "PILOT 01"
        if actor == controlled:
            name += " / ACTIVE"
        if game.phase == "aim":
            name = "AUTO-FIRE UP / NO FIRE KEY"
        if game.growth and actor == 4:
            name = "GUNSHIP / DOUBLE DAMAGE"
        if game.flight and actor == 4:
            name = f"EVASION / {game.flight:.1f}s"
        elif getattr(game, "is_floating", False) and actor == 4:
            name = f"FLOATING / {hints['float']} TO LAND"
        text(cr, name, w/2, h/2+60, 13, CYAN, True)
        for i in range(3):
            color(cr, CYAN if i < game.shields else MUTED, 1 if i < game.shields else .25)
            cr.rectangle(w/2-39+i*28, h/2+72, 22, 5)
            cr.fill()
        if game.contact_flash:
            color(cr, (.25, .02, .04), .96)
            cr.rectangle(w/2-145, h/2-38, 290, 52)
            cr.fill()
            text(cr, "COLLISION / -1 SHIELD", w/2, h/2-5, 19, WHITE, True)
    elif actor in game.enemies:
        boss = game.boss > 0
        locked = actor == game.locked_target
        color(cr, RED, .07)
        cr.paint()
        color(cr, RED, .9)
        cr.set_line_width(3)
        cr.rectangle(4, 4, w-8, h-8)
        cr.stroke()
        text(cr, "HOSTILE / TOUCH = -1 SHIELD", w/2, 65, 12, RED, True)
        if locked:
            color(cr, CYAN, .1)
            cr.paint()
            color(cr, CYAN, .8)
            cr.set_line_width(2)
            cr.rectangle(8, 8, w-16, h-16)
            cr.stroke()
        if actor in game.enemy_flashes:
            color(cr, WHITE, .18)
            cr.paint()
        cr.save()
        cr.translate(w/2, h/2-12)
        cr.scale(2.6 if boss else 1.8, 2.6 if boss else 1.8)
        enemy(cr, 0, 0, RED)
        if boss:
            color(cr, RED, .3)
            cr.arc(0, 0, 31, -t*.4, -t*.4+math.pi*1.6)
            cr.stroke()
        cr.restore()
        title = {1: "THE WINDOW DEVOURER", 2: "ARMOR FRAGMENT", 3: "DETACHED CORE"}.get(game.boss, "INTERCEPTOR")
        if game.phase == "aim":
            title = "LOCKED / STILL HOSTILE" if locked else "HOSTILE TARGET"
        text(cr, title, w/2, h/2+50, 14, RED, True)
        text(cr, f"HULL {game.enemies[actor]:02d} / GET BELOW THIS WINDOW", w/2, h/2+69, 11, WHITE, True)
    elif actor in game.enemy_flashes:
        text(cr, "ROUTE CLEAR", w/2, h/2-10, 20, CYAN, True)
        text(cr, game.kill_rewards.get(actor, "+250 POINTS"), w/2, h/2+20, 12, CYAN, True)
    elif not danger:
        text(cr, "CLEAR", w/2, h/2+5, 17, MUTED, True)

    if game.shot_flash and actor in game.shot_tiles:
        vertical = game.shot_direction in ("up", "down")
        points = [(w/2, 44), (w/2, h-48)] if vertical else [(0, h/2), (w, h/2)]
        line(cr, points, CYAN, 16, .2)
        line(cr, points, WHITE, 3, .9)

    if not ready or game.phase in ("ready", "briefing", "over", "victory") or game.paused or away:
        if actor == 0 or (player and game.phase != "ready"):
            color(cr, BG, .92)
            cr.rectangle(16, h/2-70, w-32, 145)
            cr.fill()
            if not ready:
                title, subtitle = "ASSEMBLING SECTORS", "Building nine real Hyprland tiles"
            elif game.phase == "over":
                title, subtitle = "SHIP LOST", f"SCORE {game.score:06d} / R to restart"
            elif game.phase == "victory":
                title, subtitle = "DEVOURER DEFEATED", f"SCORE {game.score:06d} / R to fly again"
            elif away or game.paused:
                title, subtitle = "PAUSED", "Return to board / Space to resume" if away else "Space to resume"
            else:
                title = lesson[2] if game.training else "OMARCHY FLIGHT PRACTICE"
                subtitle = lesson[3].format(**hints) if game.training else f"Swap windows: {hints['move']}"
            text(cr, title, w/2, h/2-26, 18, CYAN, True)
            text(cr, subtitle, w/2, h/2+3, 13, WHITE, True)
            if ready and game.phase in ("ready", "briefing"):
                detail = lesson[4].format(**hints) if game.training else "Auto-fire / use your real desktop shortcuts"
                text(cr, detail, w/2, h/2+30, 11, WHITE, True)
                text(cr, "SPACE WHEN READY", w/2, h/2+58, 14, CYAN, True)
    elif danger:
        label = "IMPACT" if impact else (f"ASTEROID / {game.asteroid_timers.get(slot, 0):.1f}s" if game.kind == "asteroid" else "LASER LOCK")
        text(cr, label, 20, 83 if actor in game.enemies else 65, 11, tint)

    if game.phase == "warning" and (game.kind != "asteroid" or slot in game.asteroid_timers):
        color(cr, tint if danger else CYAN, .8)
        progress = (game.asteroid_timers[slot] / game.asteroid_delays[slot]
                    if game.kind == "asteroid" else game.remaining/game.duration)
        cr.rectangle(20, h-61, (w-40)*max(0, progress), 3)
        cr.fill()
    tip = lesson[4].format(**hints) if game.training else f"{hints['move']} SWAP / AUTO-FIRE"
    if game.phase == "aim" and player:
        tip = game.aim_hint
    if player and game.reward_flash:
        tip = game.reward_text
    if player and game.contact_flash:
        tip = "SHOOT THE ENEMY BEFORE ENTERING ITS TILE"
    if player or actor == 0:
        text(cr, tip, w/2, h-42, 10, CYAN, True)
        text(cr, f"{hints['focus']} focus / {hints['close']} quit", w/2, h-26, 10, MUTED, True)
        text(cr, "SPACE pause / R restart / Super = Windows key", w/2, h-11, 9, MUTED, True)
    elif actor == controlled:
        text(cr, f"Focus your ship: {hints['focus']}", w/2, h-22, 12, CYAN, True)
    if actor == 4 and (not game.training or game.wave >= 16):
        color(cr, CYAN, .15)
        cr.rectangle(w-158, 47, 142, 28)
        cr.fill()
        button = "MERGE WING" if game.split else ("DEPLOY WING (30)" if game.energy >= 30 else f"CHARGING {int(game.energy)}/30")
        text(cr, button, w-87, 65, 11, CYAN, True)
    if game.burst and actor == 4:
        color(cr, CYAN, .35)
        cr.paint()
        for radius in range(60, int(max(w,h)), 100):
            color(cr, WHITE, .5)
            cr.set_line_width(4)
            cr.arc(w/2, h/2, radius + (t*250)%100, 0, math.tau)
            cr.stroke()
        text(cr, "F U L L S C R E E N   N O V A", w/2, h/2, 27, WHITE, True)

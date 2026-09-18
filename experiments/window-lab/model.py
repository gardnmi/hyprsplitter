"""Geometry-driven interaction sketches; no desktop dependencies."""
from dataclasses import dataclass
import math


@dataclass(frozen=True)
class Demo:
    name: str
    tool: str
    target: str
    rule: str
    hint: str
    result: str
    seconds: float = 3
    decay: float = 0


DEMOS = (
    Demo('Rain / Fire', 'cloud', 'fire', 'above', 'Hold the cloud above the fire.', 'Fire out. The path is safe.', decay=.07),
    Demo('Sun / Ice', 'sun', 'ice', 'above', 'Warm the ice from above.', 'Ice melted. The key is free.', seconds=4, decay=.035),
    Demo('Fan / Sailboat', 'fan', 'boat', 'left', 'Aim the fan from the left of the boat.', 'The boat reached the far shore.', seconds=4),
    Demo('Magnet / Key', 'magnet', 'key', 'near', 'Bring the magnet close to the key.', 'Key collected without crossing the gap.'),
    Demo('Rain / Seed', 'cloud', 'plant', 'above', 'Water the seed from above.', 'A climbing plant has grown.', seconds=4),
    Demo('Battery / Robot', 'battery', 'robot', 'contact', 'Touch the battery window to the robot.', 'Robot awake. A new helper!', seconds=3),
    Demo('Shield / Walker', 'shield', 'walker', 'left', 'Keep the shield left of the walker.', 'Three laser bursts blocked.', seconds=4.5, decay=.3),
    Demo('Trampoline / Walker', 'trampoline', 'jumper', 'below', 'Put the trampoline below the walker.', 'Bounced up to the high ledge.', seconds=2),
    Demo('Weight / Drawbridge', 'weight', 'bridge', 'above', 'Set the weight just above the bridge.', 'Bridge lowered. Safe to cross.', seconds=3, decay=.35),
    Demo('Lantern / Ghost', 'lantern', 'ghost', 'near', 'Bring the lantern near the hidden ghost.', 'Ghost revealed and scared away.', seconds=3, decay=.15),
)


def rect(c):
    x, y = c['at']; w, h = c['size']
    return x, y, w, h


def linked(demo, source, target):
    if source['workspace']['id'] != target['workspace']['id']:
        return False
    x, y, w, h = rect(source); a, b, u, v = rect(target)
    sx, sy, tx, ty = x+w/2, y+h/2, a+u/2, b+v/2
    overlap_x = min(x+w, a+u)-max(x,a)
    overlap_y = min(y+h, b+v)-max(y,b)
    if demo.rule == 'above':
        reach = 90 if demo.tool == 'weight' else 420
        return overlap_x >= min(w,u)*.35 and -25 <= b-y-h <= reach
    if demo.rule == 'below':
        return overlap_x >= min(w,u)*.35 and -25 <= y-b-v <= 250
    if demo.rule == 'left':
        return overlap_y >= min(h,v)*.35 and -25 <= a-x-w <= 420
    # Edge-to-edge distance permits a small window beside a large one.
    dx, dy = max(a-x-w, x-a-u, 0), max(b-y-h, y-b-v, 0)
    distance = math.hypot(dx,dy)
    if demo.rule == 'contact':
        return distance <= 12
    return distance < 95 and math.hypot(sx-tx,sy-ty) < (w+u+h+v)/4+110


class State:
    def __init__(self, index=0):
        self.index = index
        self.reset()

    @property
    def demo(self):
        return DEMOS[self.index]

    def reset(self):
        self.progress = 0.
        self.active = False
        self.won = False

    def step(self, dt, active):
        self.active = active
        if self.won:
            return
        rate = 1/self.demo.seconds if active else -self.demo.decay
        self.progress = max(0., min(1., self.progress + dt*rate))
        self.won = self.progress >= 1

"""Small independent lessons. Native window observations are the only actions."""
import random
from controls import MISSIONS
from field import SECTORS, DODGES, WARNING, MAX_ROCKS, sector

FRIENDLIES = {1, 5, 8, 11, 14}
TARGETS = set(range(16)) - FRIENDLIES - {4}


def center(rect):
    return tuple(rect['at'][i] + rect['size'][i]/2 for i in (0, 1))


def side(rect, arena):
    x, y, w, h = arena
    cx, cy = center(rect)
    # A two-window split spans one axis of the board.
    if rect['size'][1] > h*.8:
        return 'left' if cx < x+w/2 else 'right'
    if rect['size'][0] > w*.8:
        return 'top' if cy < y+h/2 else 'bottom'
    return None


class Game:
    def __init__(self, mission='asteroids', seed=None):
        self.rng = random.Random(seed)
        self.controls = {}
        self.load(mission)

    def load(self, mission):
        self.mission = mission
        self.index = next(i for i, item in enumerate(MISSIONS) if item[0] == mission)
        self.state = 'briefing'
        self.paused = False
        self.progress = 0
        self.step = 0
        self.visited = set()
        self.rocks = {}
        self.pending = []
        self.flashes = {}
        self.spawn_in = .8
        self.timer = 5.0
        self.cooldown = 0.0
        self.fired_side = None
        self.feedback = ''
        self.feedback_time = 0
        self.enemies = TARGETS.copy() if mission == 'shoot' else set()
        self.friendlies = FRIENDLIES.copy() if mission == 'shoot' else set()
        self.focused = 4
        self.ship_slot = 4
        self.geometry = {}
        self.arena = (0, 0, 1, 1)
        self.baseline_width = None
        self.hold = 0
        self.charge = 0.0
        self.blast = 0.0
        self.valid_ship = True

    def start(self):
        if self.state == 'briefing':
            self.state = 'active'
            self.visited.add(self.ship_slot)
            if 4 in self.geometry:
                self.baseline_width = self.geometry[4]['size'][0]

    def say(self, message):
        self.feedback = message
        self.feedback_time = 2.0

    def finish(self):
        self.state = 'complete'
        self.rocks.clear()
        self.pending.clear()
        self.flashes.clear()

    @property
    def safe_side(self):
        return ('top', 'right', 'bottom', 'left')[min(self.progress, 3)]

    @property
    def docking_ship_size(self):
        return min(440, self.arena[2]*.24), min(300, self.arena[3]*.34)

    @property
    def dock_rect(self):
        x, y, w, h = self.arena
        sw, sh = self.docking_ship_size
        dw, dh = sw+100, sh+100
        return x+w*.75-dw/2, y+h*.5-dh/2, dw, dh

    def in_dock(self, ship):
        x,y,w,h = self.dock_rect
        sx,sy = ship['at']; sw,sh = ship['size']
        return sx >= x and sy >= y and sx+sw <= x+w and sy+sh <= y+h

    def docking_direction(self):
        ship = self.geometry.get(4)
        if not ship:
            return 'TOWARD THE GREEN BAY'
        x,y,w,h = self.dock_rect
        cx,cy = center(ship)
        dx,dy = x+w/2-cx,y+h/2-cy
        directions = []
        if abs(dx)>25: directions.append('RIGHT' if dx>0 else 'LEFT')
        if abs(dy)>25: directions.append('DOWN' if dy>0 else 'UP')
        return ' + '.join(directions) or 'INTO THE GREEN BAY'

    def observe(self, geometry, arena, focused):
        self.geometry, self.arena, self.focused = geometry, arena, focused
        ship = geometry.get(4)
        if not ship:
            return
        x, y, w, h = arena
        cx, cy = center(ship)
        self.ship_slot = sector(ship, arena)
        mode = ship.get('fullscreen', 0)
        floating = ship.get('floating', False)
        self.valid_ship = not mode and not floating
        if self.state != 'active' or self.paused:
            return
        if self.mission == 'asteroids' and self.valid_ship:
            self.visited.add(self.ship_slot)
        elif self.mission == 'float':
            if self.step == 0 and floating and not mode:
                self.step = 1
                self.say('UNDOCKED / DRAG YOUR WINDOW INTO THE GREEN BAY')
            elif self.step in (1,2) and floating and not mode:
                self.step = 2 if self.in_dock(ship) else 1
            elif self.step == 1 and not floating and not mode:
                self.step = 0
                self.say('OUTSIDE THE BAY / UNDOCK AND TRY AGAIN')
            elif self.step == 2 and not floating and not mode:
                self.finish()
        elif self.mission == 'invasion':
            if self.step == 0 and mode == 2:
                self.step = 1
            elif self.step == 1 and mode != 2:
                self.charge = 0
                self.step = 0
                self.say('CHARGE INTERRUPTED / HOLD FULLSCREEN UNTIL CHARGED')
            elif self.step == 2 and mode == 1:
                self.step = 3
                self.blast = 0
                self.say('SECRET WEAPON RELEASED')

    def close_exits(self, actor):
        """Native close quits except for live target-practice interactions."""
        return (actor == 4 or self.mission != 'shoot' or
                self.state != 'active' or self.paused)

    def close_target(self, actor):
        if self.mission != 'shoot' or self.state != 'active' or self.paused or actor not in self.enemies:
            return False
        self.enemies.remove(actor)
        self.progress += 1
        self.say('TARGET DESTROYED / WINDOW CLOSED')
        if not self.enemies:
            self.finish()
        return True

    def spawn_rocks(self):
        available = [i for i in range(SECTORS) if i not in self.rocks and all(slot != i for _, slot in self.pending)]
        if not available or len(self.rocks) + len(self.pending) >= MAX_ROCKS:
            self.spawn_in = .3
            return
        count = min(len(available), MAX_ROCKS-len(self.rocks)-len(self.pending),
                    self.rng.choice([1, 2, 3, 4, 5, 6]))
        slots = self.rng.sample(available, count)
        # Every burst asks the pilot to move, with additional randomly placed rocks.
        if self.ship_slot in available and self.ship_slot not in slots:
            slots[0] = self.ship_slot
        together = self.rng.random() < .5
        for slot in slots:
            delay = 0 if together else self.rng.uniform(0, .8)
            self.pending.append((delay, slot))
        self.spawn_in = self.rng.uniform(1.2, 2.0)

    def advance(self, dt):
        if self.state != 'active' or self.paused:
            return
        self.feedback_time = max(0, self.feedback_time-dt)
        self.flashes = {s: t-dt for s,t in self.flashes.items() if t > dt}
        if self.mission == 'asteroids':
            # Floating/fullscreen cannot bypass the move lesson.
            if not self.valid_ship:
                return
            for slot in list(self.rocks):
                self.rocks[slot] -= dt
                if self.rocks[slot] <= 0:
                    del self.rocks[slot]
                    self.flashes[slot] = .65
                    if slot == self.ship_slot:
                        self.say('HIT / MOVE OUT BEFORE THE COUNTDOWN ENDS')
                    else:
                        self.progress += 1
                        self.say('ASTEROID DODGED')
            pending = []
            for delay, slot in self.pending:
                if delay <= dt:
                    self.rocks[slot] = WARNING  # Each appearance gets a full warning.
                else:
                    pending.append((delay-dt, slot))
            self.pending = pending
            self.spawn_in -= dt
            if self.spawn_in <= 0:
                self.spawn_rocks()
            if self.progress >= DODGES and len(self.visited) == SECTORS:
                self.finish()
        elif self.mission == 'lasers':
            if not self.valid_ship:
                return
            if self.cooldown:
                self.cooldown = max(0, self.cooldown-dt)
                return
            self.timer -= dt
            if self.timer <= 0:
                self.fired_side = self.safe_side
                if side(self.geometry[4], self.arena) == self.safe_side:
                    self.progress += 1
                    self.say('GATE CLEARED')
                    if self.progress == 4:
                        self.finish()
                else:
                    self.say('LASER HIT / TRY THIS GATE AGAIN')
                self.cooldown = 2.0
                self.timer = 5.0
        elif self.mission == 'invasion':
            if self.step == 1 and self.geometry.get(4, {}).get('fullscreen') == 2:
                self.charge = min(1, self.charge+dt/2.5)
                if self.charge >= 1:
                    self.step = 2
                    self.say('WEAPON CHARGED / READY TO RELEASE')
            elif self.step == 3:
                self.blast += dt
                if self.blast >= 3:
                    self.finish()
        elif self.mission == 'resize' and self.baseline_width:
            ship = self.geometry.get(4)
            ratio = ship['size'][0]/self.baseline_width if ship else 0
            matched = self.valid_ship and (ratio >= 1.2 if self.step == 0 else abs(ratio-1) <= .08)
            self.hold = self.hold+dt if matched else 0
            if self.hold >= .6:
                self.hold = 0
                if self.step == 0:
                    self.step = 1
                    self.say('CARGO LOADED / RESTORE CRUISING WIDTH')
                else:
                    self.finish()

    def instruction(self):
        c = self.controls
        ship = self.geometry.get(4)
        if self.mission != 'shoot' and self.focused != 4:
            return f"{c['focus']} / SELECT THE CYAN SHIP"
        if self.mission in ('asteroids', 'lasers', 'resize') and not self.valid_ship:
            mode = ship.get('fullscreen', 0) if ship else 0
            key = c['fullscreen'] if mode == 2 else c['maximize'] if mode == 1 else c['float']
            return f'{key} / RETURN TO TILING'
        if self.mission == 'asteroids':
            return f"{c['move']} / MOVE TO A CLEAR SECTOR"
        if self.mission == 'lasers':
            if self.cooldown:
                return 'NEXT GATE IN A MOMENT'
            current = side(ship, self.arena) if ship else None
            goal = self.safe_side
            if current == goal:
                return 'SAFE / HOLD THIS POSITION'
            if (current in ('left', 'right')) != (goal in ('left', 'right')):
                return f"{c['split']} / ROTATE THE TWO WINDOWS"
            direction = {'top':'up', 'bottom':'down'}.get(goal, goal)
            return f"{c.get('move_'+direction, 'Super+Shift+'+direction.upper())} / SWAP TO {goal.upper()}"
        if self.mission == 'shoot':
            if self.focused in self.friendlies:
                return f"FRIENDLY / DO NOT FIRE / {c['focus']} NEXT TARGET"
            if self.focused in self.enemies:
                return f"{c['close']} / DESTROY SELECTED SHIP"
            return f"{c['focus']} / SELECT A RED SHIP"
        if self.mission == 'float':
            mode = ship.get('fullscreen',0) if ship else 0
            if mode:
                key = c['fullscreen'] if mode == 2 else c['maximize']
                return f'{key} / EXIT THIS MODE TO DOCK'
            return (f"{c['float']} / UNDOCK YOUR SHIP",
                    f"{c['drag']} / DRAG {self.docking_direction()}",
                    f"{c['float']} / ALIGNED! DOCK NOW")[self.step]
        if self.mission == 'resize':
            return f"{c['resize']} / " + ('WIDEN TO 120%' if self.step == 0 else 'RETURN TO 100%')
        return (f"{c['fullscreen']} / CHARGE SECRET WEAPON",
                'CHARGING / STAY FULLSCREEN',
                f"{c['maximize']} / RELEASE SECRET WEAPON",
                'SHOCKWAVE / INVASION DESTROYED')[self.step]

    def status(self):
        if self.mission == 'asteroids':
            return f'SECTORS {len(self.visited)}/{SECTORS}   DODGES {min(DODGES,self.progress)}/{DODGES}'
        if self.mission == 'lasers':
            return f'GATES {self.progress}/4   SAFE HALF: {self.safe_side.upper()}'
        if self.mission == 'shoot':
            return f'ENEMIES {self.progress}/{len(TARGETS)}   PROTECT {len(FRIENDLIES)} FRIENDLIES'
        if self.mission == 'resize' and self.baseline_width and 4 in self.geometry:
            return f"SHIP WIDTH {self.geometry[4]['size'][0]/self.baseline_width:.0%}"
        if self.mission == 'float':
            return ('1 / UNDOCK', '2 / PARK IN GREEN BAY', '3 / DOCK')[self.step]
        if self.mission == 'invasion':
            return f'WEAPON CHARGE {self.charge:.0%}' if self.step < 3 else 'FLEET ELIMINATED'
        return f'STEP {self.step+1}/2'

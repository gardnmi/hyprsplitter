"""Small independent lessons. Native window observations are the only actions."""
import random
from controls import MISSIONS


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
        self.spawn_in = 1.5
        self.timer = 5.0
        self.cooldown = 0.0
        self.fired_side = None
        self.feedback = ''
        self.feedback_time = 0
        self.enemies = {0, 1, 2} if mission == 'shoot' else set()
        self.focused = 4
        self.ship_slot = 4
        self.geometry = {}
        self.arena = (0, 0, 1, 1)
        self.baseline_width = None
        self.floating_origin = None
        self.hold = 0
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
    def beacon(self):
        x, y, w, h = self.arena
        return x+w*.75, y+h*.5

    def observe(self, geometry, arena, focused):
        self.geometry, self.arena, self.focused = geometry, arena, focused
        ship = geometry.get(4)
        if not ship:
            return
        x, y, w, h = arena
        cx, cy = center(ship)
        self.ship_slot = min(2, max(0, int((cy-y)/h*3)))*3 + min(2, max(0, int((cx-x)/w*3)))
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
                self.floating_origin = center(ship)
                self.say('UNDOCKED / FLY TO THE BEACON')
            elif self.step == 1 and floating and not mode:
                bx, by = self.beacon
                moved = self.floating_origin and sum((a-b)**2 for a,b in zip(center(ship), self.floating_origin)) > 40**2
                if moved and abs(cx-bx) < w*.09 and abs(cy-by) < h*.12:
                    self.step = 2
                    self.say('BEACON REACHED / RETURN TO TILING')
            elif self.step == 1 and not floating and not mode:
                self.step = 0
                self.say('LANDED EARLY / UNDOCK TO TRY AGAIN')
            elif self.step == 2 and not floating and not mode:
                self.finish()
        elif self.mission in ('fullscreen', 'maximize'):
            expected = 2 if self.mission == 'fullscreen' else 1
            if self.step == 0 and mode == expected:
                self.step = 1
                self.say('SCAN COMPLETE / TOGGLE AGAIN TO RETURN')
            elif self.step == 1 and mode == 0:
                self.finish()

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
        available = [i for i in range(9) if i not in self.rocks and all(slot != i for _, slot in self.pending)]
        if not available:
            return
        count = min(len(available), self.rng.choice([1, 1, 2, 2, 3]))
        slots = self.rng.sample(available, count)
        # Every burst asks the pilot to move, with additional randomly placed rocks.
        if self.ship_slot in available and self.ship_slot not in slots:
            slots[0] = self.ship_slot
        together = self.rng.random() < .5
        for slot in slots:
            delay = 0 if together else self.rng.uniform(0, 1.1)
            self.pending.append((delay, slot))
        self.spawn_in = self.rng.uniform(3.8, 5.2)

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
                    self.rocks[slot] = 3.2  # Each appearance gets a full warning.
                else:
                    pending.append((delay-dt, slot))
            self.pending = pending
            self.spawn_in -= dt
            if self.spawn_in <= 0:
                self.spawn_rocks()
            if self.progress >= 6 and len(self.visited) == 9:
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
            if self.focused in self.enemies:
                return f"{c['close']} / DESTROY SELECTED SHIP"
            return f"{c['focus']} / SELECT A RED SHIP"
        if self.mission == 'float':
            return (f"{c['float']} / UNDOCK", f"{c['drag']} / CENTER SHIP ON BEACON", f"{c['float']} / LAND BACK IN TILING")[self.step]
        if self.mission == 'resize':
            return f"{c['resize']} / " + ('WIDEN TO 120%' if self.step == 0 else 'RETURN TO 100%')
        mode = ship.get('fullscreen', 0) if ship else 0
        expected = 2 if self.mission == 'fullscreen' else 1
        if mode and mode != expected:
            key = c['fullscreen'] if mode == 2 else c['maximize']
            return f'{key} / EXIT THIS MODE FIRST'
        return f"{c[self.mission]} / " + ('BEGIN SCAN' if self.step == 0 else 'RETURN TO TILING')

    def status(self):
        if self.mission == 'asteroids':
            return f'SECTORS {len(self.visited)}/9   DODGES {min(6,self.progress)}/6'
        if self.mission == 'lasers':
            return f'GATES {self.progress}/4   SAFE HALF: {self.safe_side.upper()}'
        if self.mission == 'shoot':
            return f'TARGETS CLOSED {self.progress}/3'
        if self.mission == 'resize' and self.baseline_width and 4 in self.geometry:
            return f"SHIP WIDTH {self.geometry[4]['size'][0]/self.baseline_width:.0%}"
        return f'STEP {self.step+1}/' + ('3' if self.mission == 'float' else '2')

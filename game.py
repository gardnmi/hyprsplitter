"""Deterministic game rules, independent of GTK and Hyprland."""

import random


class Game:
    def __init__(self, seed=None):
        self.rng = random.Random(seed)
        self.restart()

    def restart(self):
        self.ship = 4
        self.shields = 3
        self.score = 0
        self.wave = 0
        self.phase = "ready"
        self.remaining = 0.0
        self.duration = 1.0
        self.hazards = set()
        self.asteroid_timers = {}
        self.asteroid_delays = {}
        self.asteroid_flashes = {}
        self.asteroid_hits = set()
        self.kind = "laser"
        self.axis = "row"
        self.paused = False
        self.hit = False
        self.energy = 100.0
        self.growth = 0.0
        self.flight = 0.0
        self.burst = 0.0
        self.split = False
        self.wing = None
        self.boss = 0
        self.enemies = {0: 3, 2: 3}
        self.shot_cooldown = 0.0
        self.shot_flash = 0.0
        self.shot_direction = "up"
        self.shot_tiles = set()
        self.message = "IJKL FIRE / G GROW / E SPLIT / F FLOAT / X FULLSCREEN"

    def start(self):
        if self.phase == "ready":
            self.next_wave()

    def next_wave(self):
        self.wave += 1
        self.hit = False
        self.phase = "warning"
        if self.wave == 5 and self.boss == 0:
            self.boss = 1
            self.enemies = {0: 18}
            self.message = "THE WINDOW DEVOURER / BREAK ITS ARMOR"
        elif self.boss == 0:
            for index in (0, 2):
                self.enemies.setdefault(index, 3)
        # Start at showcase intensity: no slow opening waves.
        self.duration = max(0.65, 0.95 - (self.wave - 1) * 0.015)
        self.remaining = self.duration
        self.kind = "asteroid" if self.wave % 3 == 0 else "laser"
        self.asteroid_timers.clear()
        self.asteroid_delays.clear()
        self.asteroid_flashes.clear()
        self.asteroid_hits.clear()
        if self.kind == "asteroid":
            others = [i for i in range(9) if i != self.ship]
            self.hazards = {self.ship, *self.rng.sample(others, 5)}
            order = self.rng.sample(sorted(self.hazards), len(self.hazards))
            deadline = self.duration
            for slot in order:
                self.asteroid_timers[slot] = deadline
                deadline += self.rng.uniform(.18, .34)
            self.asteroid_delays = self.asteroid_timers.copy()
        else:
            self.axis = self.rng.choice(("row", "column"))
            ship_lane = self.ship // 3 if self.axis == "row" else self.ship % 3
            safe_lane = self.rng.choice([i for i in range(3) if i != ship_lane])
            self.hazards = {i for i in range(9) if (i // 3 if self.axis == "row" else i % 3) != safe_lane}

    def neighbor(self, direction):
        dr, dc = {"left": (0, -1), "right": (0, 1), "up": (-1, 0), "down": (1, 0)}[direction]
        row, col = divmod(self.ship, 3)
        row, col = row + dr, col + dc
        return row * 3 + col if 0 <= row < 3 and 0 <= col < 3 else None

    def advance(self, dt):
        if self.paused or self.phase in ("ready", "over"):
            return
        if self.phase == "victory":
            self.burst = max(0, self.burst - dt)
            return
        self.energy = min(100, self.energy + dt * 9)
        self.shot_cooldown = max(0, self.shot_cooldown - dt)
        self.shot_flash = max(0, self.shot_flash - dt)
        self.growth = max(0, self.growth - dt)
        self.flight = max(0, self.flight - dt)
        self.burst = max(0, self.burst - dt)
        if self.burst:
            return
        self.asteroid_flashes = {slot: remaining-dt for slot, remaining in self.asteroid_flashes.items() if remaining > dt}
        if self.kind == "asteroid" and self.phase == "warning":
            self.advance_asteroids(dt)
            return
        self.remaining -= dt
        if self.remaining > 0:
            return
        if self.phase == "warning":
            self.hit = (not self.flight and self.ship in self.hazards) or (self.split and self.wing in self.hazards)
            if self.hit:
                self.shields -= 1
            else:
                self.score += 100
            self.phase = "impact"
            self.remaining = 0.25
        elif self.phase == "impact":
            self.phase = "over" if self.shields == 0 else "cooldown"
            self.remaining = 0.12
            self.hazards = set()
        else:
            self.next_wave()

    def advance_asteroids(self, dt):
        for slot in list(self.asteroid_timers):
            self.asteroid_timers[slot] -= dt
            if self.asteroid_timers[slot] > 1e-9:
                continue
            del self.asteroid_timers[slot]
            self.hazards.discard(slot)
            self.asteroid_flashes[slot] = .32
            hit = (not self.flight and self.ship == slot) or (self.split and self.wing == slot)
            if hit:
                self.shields -= 1
                self.asteroid_hits.add(slot)
            else:
                self.score += 20
            if self.shields <= 0:
                self.phase = "over"
                self.hazards.clear()
                self.asteroid_timers.clear()
                return
        if self.asteroid_timers:
            self.remaining = min(self.asteroid_timers.values())
        else:
            self.phase = "impact"
            self.remaining = .25

    @property
    def playing(self):
        return not self.paused and self.phase not in ("ready", "over", "victory")

    def ability(self, name):
        if not self.playing or self.burst:
            return False
        if name == "split" and self.split:
            self.split = False
            self.wing = None
            self.message = "WING MERGED"
            return True
        if name == "float" and self.flight:
            self.flight = 0
            self.message = "LANDING"
            return True
        cost = {"grow": 25, "split": 30, "float": 35, "fullscreen": 100}[name]
        if self.energy < cost or (name == "grow" and self.growth):
            self.message = "RECHARGING / SHOOT ENEMIES FOR ENERGY"
            return False
        self.energy -= cost
        if name == "grow":
            self.growth = 5
            self.message = "GUNSHIP / DOUBLE DAMAGE FOR 5 SECONDS"
        elif name == "split":
            self.split = True
            self.message = "WING DEPLOYED / TAB SWITCHES SHIPS"
        elif name == "float":
            self.flight = 3
            self.message = "FREE FLIGHT / 3 SECONDS OF EVASION"
        else:
            self.burst = .9
            # Snapshot victims: a phase change cannot damage newly spawned armor.
            victims = list(self.enemies)
            stage = self.boss
            for enemy in victims:
                if self.boss != stage:
                    break
                self.damage(enemy, 8)
            self.message = "FULLSCREEN NOVA"
        return True

    def fire(self, direction, targets, tiles):
        if not self.playing or self.shot_cooldown or self.burst:
            return False
        self.shot_direction = direction
        self.shot_flash = .16
        self.shot_tiles = set(tiles)
        self.shot_cooldown = .20 if self.growth else .32
        stage = self.boss
        for target in targets:
            if self.boss != stage:
                break
            self.damage(target, 2 if self.growth else 1)
        return True

    def damage(self, enemy, amount):
        if enemy not in self.enemies:
            return
        self.enemies[enemy] -= amount
        if self.enemies[enemy] > 0:
            return
        del self.enemies[enemy]
        self.score += 250
        self.energy = min(100, self.energy + 20)
        if self.boss == 1:
            self.boss = 2
            self.enemies = {0: 6, 10: 6, 11: 6}
            self.message = "ARMOR SHATTERED / THREE HOSTILE WINDOWS"
        elif self.boss == 2 and not self.enemies:
            self.boss = 3
            self.enemies = {0: 12}
            self.message = "CORE DETACHED / TRACK THE FLOATING BOSS"
        elif self.boss == 3 and not self.enemies:
            self.boss = 4
            self.phase = "victory"
            self.hazards.clear()
            self.asteroid_timers.clear()
            self.asteroid_flashes.clear()
            self.score += 2000
            self.message = "WINDOW DEVOURER DEFEATED"

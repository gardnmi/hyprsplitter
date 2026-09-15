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
        self.kind = "laser"
        self.axis = "row"
        self.paused = False
        self.hit = False

    def start(self):
        if self.phase == "ready":
            self.next_wave()

    def next_wave(self):
        self.wave += 1
        self.hit = False
        self.phase = "warning"
        # Start at showcase intensity: no slow opening waves.
        self.duration = max(0.65, 0.95 - (self.wave - 1) * 0.015)
        self.remaining = self.duration
        self.kind = "asteroid" if self.wave % 3 == 0 else "laser"
        if self.kind == "asteroid":
            others = [i for i in range(9) if i != self.ship]
            self.hazards = {self.ship, *self.rng.sample(others, 5)}
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
        self.remaining -= dt
        if self.remaining > 0:
            return
        if self.phase == "warning":
            self.hit = self.ship in self.hazards
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

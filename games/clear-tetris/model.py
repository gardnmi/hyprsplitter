"""Deterministic falling-block rules, independent of the desktop."""
import random

WIDTH, HEIGHT = 10, 20
SHAPES = {
    'I': ((0, 1), (1, 1), (2, 1), (3, 1)),
    'O': ((1, 0), (2, 0), (1, 1), (2, 1)),
    'T': ((1, 0), (0, 1), (1, 1), (2, 1)),
    'S': ((1, 0), (2, 0), (0, 1), (1, 1)),
    'Z': ((0, 0), (1, 0), (1, 1), (2, 1)),
    'J': ((0, 0), (0, 1), (1, 1), (2, 1)),
    'L': ((2, 0), (0, 1), (1, 1), (2, 1)),
}


class Game:
    def __init__(self, seed=None):
        self.rng = random.Random(seed)
        self.board = [[None] * WIDTH for _ in range(HEIGHT)]
        self.queue = []
        self.score = self.lines = 0
        self.over = False
        self.held = None
        self.hold_used = False
        self.gravity = self.grounded = 0.
        self.lock_resets = 0
        self._fill_queue()
        self.spawn()

    @property
    def level(self):
        return 1 + self.lines // 10

    @property
    def interval(self):
        return max(.075, .8 * .82 ** (self.level - 1))

    def _fill_queue(self):
        if len(self.queue) < 7:
            bag = list(SHAPES)
            self.rng.shuffle(bag)
            self.queue.extend(bag)

    def spawn(self, kind=None):
        if kind is None:
            kind = self.queue.pop(0)
            self._fill_queue()
        self.kind = kind
        self.shape = SHAPES[kind]
        self.x, self.y = 3, 0
        self.gravity = self.grounded = 0.
        self.lock_resets = 0
        if not self.fits(self.shape, self.x, self.y):
            self.over = True

    def cells(self, y=None):
        return [(self.x + x, (self.y if y is None else y) + dy)
                for x, dy in self.shape]

    def fits(self, shape, x, y):
        return all(0 <= x + dx < WIDTH and 0 <= y + dy < HEIGHT
                   and self.board[y + dy][x + dx] is None for dx, dy in shape)

    def _reset_lock(self):
        if self.lock_resets < 15 and not self.fits(self.shape, self.x, self.y + 1):
            self.grounded = 0.
            self.lock_resets += 1

    def move(self, dx, dy=0):
        if self.over or not self.fits(self.shape, self.x + dx, self.y + dy):
            return False
        self._reset_lock()
        self.x += dx
        self.y += dy
        return True

    def rotate(self, clockwise=True):
        if self.over or self.kind == 'O':
            return False
        size = 4 if self.kind == 'I' else 3
        shape = tuple((size - 1 - y, x) if clockwise else (y, size - 1 - x)
                      for x, y in self.shape)
        # Small wall/floor kicks keep rotations usable at the board edges.
        for dx, dy in ((0, 0), (-1, 0), (1, 0), (-2, 0), (2, 0), (0, -1), (0, -2)):
            if self.fits(shape, self.x + dx, self.y + dy):
                self._reset_lock()
                self.shape = shape
                self.x += dx
                self.y += dy
                return True
        return False

    def ghost_y(self):
        y = self.y
        while self.fits(self.shape, self.x, y + 1):
            y += 1
        return y

    def hard_drop(self):
        if self.over:
            return
        target = self.ghost_y()
        self.score += (target - self.y) * 2
        self.y = target
        self.lock()

    def hold(self):
        if self.over or self.hold_used:
            return
        previous = self.held
        self.held = self.kind
        self.spawn(previous)
        self.hold_used = True

    def lock(self):
        for x, y in self.cells():
            self.board[y][x] = self.kind
        remaining = [row for row in self.board if not all(row)]
        cleared = HEIGHT - len(remaining)
        self.score += (0, 100, 300, 500, 800)[cleared] * self.level
        self.lines += cleared
        self.board = [[None] * WIDTH for _ in range(cleared)] + remaining
        self.hold_used = False
        self.spawn()

    def update(self, dt, soft_drop=False):
        if self.over:
            return
        dt = min(max(dt, 0.), .1)
        self.gravity += dt
        interval = min(.045, self.interval) if soft_drop else self.interval
        while self.gravity >= interval:
            self.gravity -= interval
            if self.move(0, 1) and soft_drop:
                self.score += 1
        if self.fits(self.shape, self.x, self.y + 1):
            self.grounded = 0.
        else:
            self.grounded += dt
            if self.grounded >= .5:
                self.lock()

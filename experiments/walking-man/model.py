"""Level one: carry the walker past danger by rearranging his room."""


class Level:
    def __init__(self, number=1):
        self.number = number
        self.reset()

    def reset(self):
        self.order = ['path', 'fire', 'goal']
        self.room = 'path'
        self.x = .12
        self.status = 'ready'
        self.flames = [1.] * 12
        self.extinguished = False
        self.wet_cells = [False] * 12
        self.wet = False

    @property
    def heat(self):
        return sum(self.flames) / len(self.flames)

    def swap(self):
        if self.number == 1 and self.status in ('ready', 'walking'):
            self.order[:2] = reversed(self.order[:2])

    def step(self, dt, geometry=None):
        if self.status != 'walking':
            return
        if self.number == 2 and not self.extinguished:
            self.flames = [max(0., heat - .32 * dt) if wet else min(1., heat + .045 * dt)
                           for heat, wet in zip(self.flames, self.wet_cells)]
            if max(self.flames) < .015:
                self.flames = [0.] * 12
                self.extinguished = True
        self.x += dt / 9
        # Transfer the walker into the real neighboring route tile, carrying
        # any remaining distance across the compositor's decorative gap.
        if self.x >= 1:
            if geometry:
                current = geometry[self.room]
                right = current['at'][0] + current['size'][0]
                floor = current['at'][1] + current['size'][1] - 95
                neighbors = [r for r in ('path', 'fire', 'goal')
                             if r != self.room and geometry[r]['at'][0] >= right - 2
                             and abs(geometry[r]['at'][1] + geometry[r]['size'][1] - 95 - floor) < 30]
                if not neighbors:
                    self.x = 1
                    return
                target = min(neighbors, key=lambda r: geometry[r]['at'][0])
                self.x = (self.x - 1) * current['size'][0] / geometry[target]['size'][0]
                self.room = target
            else:
                index = self.order.index(self.room)
                self.room = self.order[min(index + 1, 2)]
                self.x -= 1
        if self.room == 'fire' and .30 <= self.x <= .76 and self.heat > .001:
            self.status = 'lost'
        elif self.room == 'goal' and self.x >= .65:
            self.status = 'won'


def rain_cells(cloud, fire):
    """Each flame cools only when directly under the cloud's visible rain."""
    if cloud['workspace']['id'] != fire['workspace']['id']:
        return [False] * 12
    cx, cy = cloud['at']
    cw, ch = cloud['size']
    fx, fy = fire['at']
    fw, fh = fire['size']
    above = cy + ch <= fy + fh - 125
    left, right = cx + cw * .25, cx + cw * .75
    return [above and left <= fx + fw * (.32 + .36 * i / 11) <= right for i in range(12)]


def rain_hits(cloud, fire):
    return any(rain_cells(cloud, fire))

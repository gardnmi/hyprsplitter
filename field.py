"""Shared geometry and pacing for the asteroid field."""
COLUMNS = 6
ROWS = 4
SECTORS = COLUMNS * ROWS
DODGES = 12
WARNING = 2.6
MAX_ROCKS = 10


def sector(rect, arena):
    x, y, w, h = arena
    cx = rect['at'][0] + rect['size'][0]/2
    cy = rect['at'][1] + rect['size'][1]/2
    return min(ROWS-1, max(0, int((cy-y)/h*ROWS)))*COLUMNS + min(COLUMNS-1, max(0, int((cx-x)/w*COLUMNS)))


def grid_steps(columns=COLUMNS, rows=ROWS):
    # Keep actor 4 as the pilot, starting near the center of the larger board.
    middle = (rows//2)*columns + columns//2
    def actor(slot):
        return middle if slot == 4 else 4 if slot == middle else slot
    steps = [(actor(0), None, None, None)]
    for col in range(1, columns):
        steps.append((actor(col), actor(col-1), 'r', 2/(columns-col+1)))
    for col in range(columns):
        for row in range(1, rows):
            steps.append((actor(row*columns+col), actor((row-1)*columns+col), 'd', 2/(rows-row+1)))
    return steps

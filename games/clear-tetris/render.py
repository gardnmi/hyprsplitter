"""Code-drawn glass board; empty cells have zero alpha by default."""
import cairo

from model import WIDTH, HEIGHT, SHAPES

WINDOW_W, WINDOW_H = 372, 684
BOARD_X, BOARD_Y, CELL = 16, 110, 26
COLORS = {
    'I': (.24, .88, .96), 'O': (1., .82, .29), 'T': (.76, .52, 1.),
    'S': (.40, .92, .64), 'Z': (1., .40, .50), 'J': (.38, .60, 1.),
    'L': (1., .65, .32),
}


def panel(c, x, y, w, h, alpha=.82):
    c.set_source_rgba(.025, .045, .065, alpha)
    c.rectangle(x, y, w, h)
    c.fill()


def text(c, x, y, label, size=11, color=(.84, .91, .95), alpha=1.):
    c.select_font_face('monospace', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    c.set_font_size(size)
    # A small outline keeps labels legible over both bright and dark video.
    c.move_to(x, y)
    c.text_path(str(label))
    c.set_source_rgba(.02, .03, .05, .8)
    c.set_line_width(2.5)
    c.stroke_preserve()
    c.set_source_rgba(*color, alpha)
    c.fill()


def block(c, x, y, kind, size=CELL, ghost=False):
    color = COLORS[kind]
    c.rectangle(x + 2, y + 2, size - 4, size - 4)
    c.set_source_rgba(*color, .06 if ghost else .78)
    c.fill_preserve()
    c.set_source_rgba(*color, .65 if ghost else 1.)
    c.set_line_width(1.2)
    c.stroke()
    if not ghost:
        c.set_source_rgba(1, 1, 1, .36)
        c.rectangle(x + 4, y + 4, size - 8, 2)
        c.fill()


def preview(c, kind, x, y):
    if kind:
        shape = SHAPES[kind]
        left, top = min(a for a, b in shape), min(b for a, b in shape)
        for a, b in shape:
            block(c, x + (a - left) * 16, y + (b - top) * 16, kind, 16)


def draw(c, game, paused=True, tint=0., grid=True):
    c.set_operator(cairo.OPERATOR_SOURCE)
    c.set_source_rgba(0, 0, 0, 0)
    c.paint()
    c.set_operator(cairo.OPERATOR_OVER)

    panel(c, 0, 0, WINDOW_W, 92)
    c.set_source_rgb(.24, .88, .96)
    c.rectangle(0, 0, 3, 92)
    c.fill()
    text(c, 16, 26, 'CLEAR / TETRIS', 17)
    text(c, 17, 47, 'A LITTLE SPACE TO PLAY', 9, (.48, .71, .77))
    text(c, 318, 25, 'II', 14)
    text(c, 349, 25, 'X', 14)
    text(c, 17, 76, f'{game.score:06d}', 20)
    text(c, 132, 74, f'LINES {game.lines:03d}', 11)
    text(c, 259, 74, f'LEVEL {game.level:02d}', 11)

    board_w, board_h = WIDTH * CELL, HEIGHT * CELL
    if tint:
        panel(c, BOARD_X, BOARD_Y, board_w, board_h, tint)
    c.set_source_rgba(.69, .89, .94, .45)
    c.set_line_width(1.)
    c.rectangle(BOARD_X - .5, BOARD_Y - .5, board_w + 1, board_h + 1)
    c.stroke()
    if grid:
        c.set_source_rgba(.75, .92, 1., .085)
        for x in range(1, WIDTH):
            c.move_to(BOARD_X + x * CELL, BOARD_Y)
            c.line_to(BOARD_X + x * CELL, BOARD_Y + board_h)
        for y in range(1, HEIGHT):
            c.move_to(BOARD_X, BOARD_Y + y * CELL)
            c.line_to(BOARD_X + board_w, BOARD_Y + y * CELL)
        c.stroke()
    for y, row in enumerate(game.board):
        for x, kind in enumerate(row):
            if kind:
                block(c, BOARD_X + x * CELL, BOARD_Y + y * CELL, kind)
    if not game.over:
        for x, y in game.cells(game.ghost_y()):
            block(c, BOARD_X + x * CELL, BOARD_Y + y * CELL, game.kind, ghost=True)
        for x, y in game.cells():
            block(c, BOARD_X + x * CELL, BOARD_Y + y * CELL, game.kind)

    panel(c, 288, 110, 84, 278, .66)
    text(c, 299, 129, 'HOLD', 10)
    preview(c, game.held, 297, 145)
    text(c, 299, 202, 'NEXT', 10)
    for index, kind in enumerate(game.queue[:3]):
        preview(c, kind, 297, 218 + index * 54)
    panel(c, 288, 403, 84, 151, .66)
    for index, label in enumerate(('P PAUSE', 'C HOLD', 'Z / UP', 'ROTATE', 'SPACE', 'DROP', 'T TINT', 'G GRID')):
        text(c, 296, 422 + index * 17, label, 9)

    panel(c, 0, 644, WINDOW_W, 40)
    text(c, 16, 661, 'ARROWS MOVE / DOWN SOFT DROP', 10)
    text(c, 16, 677, 'DRAG HEADER / R RESET / ESC EXIT', 9, (.48, .71, .77))

    if paused or game.over:
        panel(c, 32, 318, 228, 86, .94)
        text(c, 50, 347, 'GAME OVER' if game.over else 'TAKE YOUR TIME', 18)
        text(c, 50, 374, 'R / PLAY AGAIN' if game.over else 'CLICK HERE / RESUME', 11)
        if not game.over:
            text(c, 50, 391, 'OR PRESS P / ENTER', 9, (.48, .71, .77))

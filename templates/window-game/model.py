"""Pure gameplay: put the entire ship window inside the dock."""


def docked(ship, dock):
    x, y, w, h = ship
    dx, dy, dw, dh = dock
    return dx <= x and dy <= y and x+w <= dx+dw and y+h <= dy+dh

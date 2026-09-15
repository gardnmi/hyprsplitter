"""Geometry shared by the controller and tests. Rectangles are global logical pixels."""


def center(rect):
    x, y = rect["at"]
    w, h = rect["size"]
    return x + w / 2, y + h / 2


def overlaps(first, second):
    x, y = first["at"]
    w, h = first["size"]
    a, b = second["at"]
    c, d = second["size"]
    return x < a+c and a < x+w and y < b+d and b < y+h


def ahead(source, target, direction):
    """Distance to a rectangle intersected by a cardinal ray; None if not aligned."""
    x, y = center(source)
    tx, ty = target["at"]
    tw, th = target["size"]
    if direction == "up" and ty + th <= y and tx <= x <= tx + tw:
        return y - (ty + th)
    if direction == "down" and ty >= y and tx <= x <= tx + tw:
        return ty - y
    if direction == "left" and tx + tw <= x and ty <= y <= ty + th:
        return x - (tx + tw)
    if direction == "right" and tx >= x and ty <= y <= ty + th:
        return tx - x
    return None


def neighbor(geometry, source, direction, excluded=()):
    options = []
    for index, rect in geometry.items():
        if index == source or rect.get("floating"):
            continue
        distance = ahead(geometry[source], rect, direction)
        if distance is not None:
            options.append((distance, index))
    closest = min(options)[1] if options else None
    return None if closest in excluded else closest


def firing_lane(geometry, source, enemies, direction):
    options = []
    for index, rect in geometry.items():
        if index == source:
            continue
        distance = ahead(geometry[source], rect, direction)
        if distance is not None:
            options.append((distance, index))
    options.sort()
    path = [source]
    for _, index in options:
        path.append(index)
        if index in enemies:
            return index, path
    return None, path


def aim_guidance(geometry, source, enemies):
    target, _ = firing_lane(geometry, source, enemies, "up")
    if target is not None:
        return target, "TARGET LOCKED / AUTO-FIRING UP"
    if not enemies:
        return None, "TARGETS CLEAR"
    sx, sy = center(geometry[source])
    candidates = [i for i in enemies if i in geometry]
    if not candidates:
        return None, "AUTO-FIRE UP / GET BELOW A TARGET"
    nearest = min(candidates, key=lambda i: sum((a-b)**2 for a, b in zip(center(geometry[i]), (sx, sy))))
    target_rect = geometry[nearest]
    tx, ty = target_rect["at"]
    tw, th = target_rect["size"]
    if ty+th > sy:
        return None, "MOVE BELOW THE RED TARGET"
    return None, "MOVE RIGHT TO LINE UP" if sx < tx else "MOVE LEFT TO LINE UP"

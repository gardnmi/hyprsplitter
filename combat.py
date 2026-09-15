"""Geometry shared by the controller and tests. Rectangles are global logical pixels."""


def center(rect):
    x, y = rect["at"]
    w, h = rect["size"]
    return x + w / 2, y + h / 2


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

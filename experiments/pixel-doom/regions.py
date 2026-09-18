"""Positive-area subdivisions of DOOM's native 320 by 200 image."""


def fixed_regions(count):
    if not 40 <= count <= 64000:
        raise ValueError('Use 40 through 64,000 regions')
    boxes=[((i%8)*40,(i//8)*40,(i%8+1)*40,(i//8+1)*40) for i in range(40)]
    while len(boxes)<count:
        remaining=count-len(boxes);refined=[]
        for box in boxes:
            children=split_region(box,remaining)
            remaining-=len(children)-1;refined.extend(children)
        boxes=refined
    return boxes


def split_region(box, remaining):
    x0, y0, x1, y1 = box
    if remaining < 1 or (x1 - x0 == 1 and y1 - y0 == 1):
        return [box]
    xm, ym = (x0 + x1) // 2, (y0 + y1) // 2
    if remaining == 1 or y1 - y0 == 1:
        if x1 - x0 > 1:
            return [(x0, y0, xm, y1), (xm, y0, x1, y1)]
        return [(x0, y0, x1, ym), (x0, ym, x1, y1)]
    if x1 - x0 == 1:
        return [(x0, y0, x1, ym), (x0, ym, x1, y1)]
    boxes = [(x0, y0, xm, ym), (xm, y0, x1, ym)]
    if remaining == 2:
        return boxes + [(x0, ym, x1, y1)]
    return boxes + [(x0, ym, xm, y1), (xm, ym, x1, y1)]

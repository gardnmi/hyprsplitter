"""Read shortcut labels without installing, replacing, or intercepting bindings."""


def shortcut_labels(bindings):
    labels = {
        "move": "Super+Shift+arrows", "focus": "Super+arrows",
        "float": "Super+T", "split": "Super+J", "fullscreen": "Super+F",
        "maximize": "Super+Alt+F", "resize": "Super+- / Super+=",
        "close": "Super+W", "drag": "Super+left-drag",
    }
    descriptions = {"Full screen": "fullscreen", "Full width": "maximize",
                    "Toggle window floating/tiling": "float", "Toggle window split": "split",
                    "Close window": "close"}
    for binding in bindings:
        action = descriptions.get(binding.get("description"))
        if not action or binding.get("submap") or not binding.get("key"):
            continue
        mask = binding.get("modmask", 0)
        mods = [name for bit, name in ((64, "Super"), (4, "Ctrl"), (8, "Alt"), (1, "Shift")) if mask & bit]
        labels[action] = "+".join(mods + [binding["key"].upper()])
    return labels


LESSONS = [
    (1, "move", "01 / MOVE THE WINDOW", "Focus your ship: {focus}", "Swap into the clear lane: {move}"),
    (4, "asteroids", "02 / RANDOM ASTEROIDS", "Rocks appear alone or in small groups.", "Watch each countdown; cleared sectors are safe."),
    (7, "shoot", "03 / SHOOTING PRACTICE", "Your ship shoots UP automatically. No fire key.", "Get below the red target. No attacks in this lesson."),
    (10, "float", "04 / FLOAT AND LAND", "Toggle floating: {float}", "Fly with {drag}; toggle again to land."),
    (13, "grow", "05 / RESIZE YOUR SHIP", "Resize: {resize} (Shift changes height)", "A larger ship deals double damage."),
    (16, "split", "06 / SPLIT ORIENTATION", "Click DEPLOY WING to add a second window.", "{split} rotates the split; {focus} selects a ship."),
    (19, "fullscreen", "07 / FULLSCREEN", "Fullscreen attack: {fullscreen}", "Maximize: {maximize}. These are different modes."),
    (22, "boss", "08 / PUT IT TOGETHER", "The boss combines shooting and window abilities.", "Break its armor, fragments, then floating core."),
]


def lesson_for(wave):
    return next(lesson for lesson in reversed(LESSONS) if wave >= lesson[0])

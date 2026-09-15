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
                    "Close window": "close", "Swap window to the left": "move_left",
                    "Swap window to the right": "move_right", "Swap window up": "move_up",
                    "Swap window down": "move_down"}
    for binding in bindings:
        action = descriptions.get(binding.get("description"))
        if not action or binding.get("submap") or not binding.get("key"):
            continue
        mask = binding.get("modmask", 0)
        mods = [name for bit, name in ((64, "Super"), (4, "Ctrl"), (8, "Alt"), (1, "Shift")) if mask & bit]
        labels[action] = "+".join(mods + [binding["key"].upper()])
    return labels


MISSIONS = [
    ("asteroids", "01 / ASTEROID FIELD", "Move your ship through all nine sectors.", "{move} to move your ship", "Visit 9 sectors and dodge 6 asteroid impacts."),
    ("lasers", "02 / LASER GATES", "Two windows. Get your ship into the safe half.", "{split} rotates / {move} swaps", "Clear 4 gates. Each miss retries the same gate."),
    ("shoot", "03 / TARGET PRACTICE", "Focus a red ship, then close its window.", "{focus} to aim / {close} to fire", "Close all 3 red ships. Keep the cyan ship."),
    ("float", "04 / DOCKING", "Undock, fly to the beacon, then land.", "{float} to float / {drag} to fly", "Follow one docking instruction at a time."),
    ("resize", "05 / CARGO BAY", "Widen your ship, then return it to cruising size.", "{resize} changes width", "Match the marked width. No time limit."),
    ("fullscreen", "06 / DEEP SPACE SCAN", "Open your ship fullscreen, then return to tiling.", "{fullscreen} toggles fullscreen", "Complete one scan. No time limit."),
    ("maximize", "07 / PANORAMA", "Maximize your ship, then return to tiling.", "{maximize} toggles maximize", "Keep the desktop bar visible during the panorama."),
]

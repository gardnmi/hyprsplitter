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
    ("asteroids", "01 / ASTEROID FIELD", "Move your ship through a 24-sector asteroid field.", "{move} to move your ship", "Visit 24 sectors and dodge 12 asteroid impacts."),
    ("lasers", "02 / LASER GATES", "Two windows. Get your ship into the safe half.", "{split} rotates / {move} swaps", "Clear 4 gates. Each miss retries the same gate."),
    ("shoot", "03 / TARGET PRACTICE", "Destroy 10 red ships. Protect the 5 green friendlies.", "{focus} to aim / {close} to fire", "Red = enemy. Green = friendly. Check before firing."),
    ("float", "04 / DOCKING", "Park your ship window inside the green docking bay.", "{float} to undock / {drag} to steer", "When the bay says ALIGNED, press {float} to dock."),
    ("resize", "05 / CARGO BAY", "Widen your ship, then return it to cruising size.", "{resize} changes width", "Match the marked width. No time limit."),
    ("invasion", "06 / SECRET WEAPON", "A massive invasion is approaching. Charge the weapon.", "{fullscreen} charges / {maximize} releases", "Wait for CHARGED, then release the blast."),
]

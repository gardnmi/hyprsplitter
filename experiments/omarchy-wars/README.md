# Omarchy: Zero Day

An Omatari desktop invasion shooter. Only the Omarchy installer appears at first.
A fictional install sets a new record, then a flashing intrusion warning interrupts
it. Eight real enemy windows erupt around the installer, in varied positions and
sizes. Each intrusion uses a transparent native window with a visibly tilted frame and
title bar. The underlying Hyprland surface remains rectangular; enemy positions
and projectile collision stay in desktop coordinates. Layouts use uneven spacing
and varied proportions. Ship and enemy art and hitboxes are about half the
original prototype size.

```sh
python experiments/omarchy-wars/main.py
# Or select ZERO DAY in ./arcade.
```

Your Omarchy O ship defends the installer. Invaders leave their spawn windows,
fly across the desktop, and enter your installer to attack. Both sides fire across
the desktop through a transparent gameplay overlay that catches firing clicks.

The fictional install lasts **9.99 seconds**, followed by its record screen and
a **4.5-second** animated warning. The opening introduces two windows with one
enemy each. Pairs arrive at 12, 24, and 36 seconds, reaching eight spawn slots.
Enemy gunfire begins at 12 seconds; movement, reinforcement rate, and health
ramp over one minute. Window health rises from 10 to 22 hits and the enemy cap
from 8 to 44. Shoot a window to stop its reinforcements; escaped ships remain.

Replacement delays shrink from 5–10 seconds to 2–4 seconds as difficulty rises.
If all windows are destroyed, the next replacement appears immediately.
Pausing freezes timers. R restarts the story and resets upgrades.

Drifting pickups inside the installer upgrade your parallel laser volley from
one to two, three, then four beams. Collect them by touching them. Upgrades last
for that attempt; no more spawn once you reach four lasers.

The six fictional enemy-window factions parody arguments about Linux desktops:
Bloat Patrol, Arch Gatekeeper, Dotfile Tribunal, Default Police, Nix Purist, and
Discourse Storm. See [SATIRE.md](SATIRE.md) for references and context.

- Space or click: start the fictional install (no system changes).
- WASD / arrows: move inside the installer. Mouse: aim; hold left button: fire.
- Space: invulnerable dash with a 1.5-second recharge.
- P: pause/resume. Leaving the workspace freezes the simulation.
- R: close the invasion windows and restart the install.
- Escape / native close: exit the entire game and return to the previous workspace.

Best score: `$XDG_STATE_HOME/hyprsplitter/zero-day.json`, defaulting to
`~/.local/state/hyprsplitter/zero-day.json`. Temporary window rules are removed
on exit. No desktop configuration is changed.

Tests: `python -m unittest discover -s experiments/omarchy-wars -p test_model.py`.

Enemies crossing empty desktop space become neon-green digital skeletons with
unfilled wire edges, bright vertices, and falling binary fragments. They regain
their normal colors and details inside window scenes. The transparent gameplay
window receives firing clicks over empty space, preventing desktop click-through.

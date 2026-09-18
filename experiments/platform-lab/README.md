# Floating window platform puzzles

All puzzle windows now **start floating**. Move and resize them freely to
construct a route. The man keeps walking while his occupied window moves;
only Space or leaving the workspace pauses the game.

```sh
cd ~/Projects/hyprsplitter
python experiments/platform-lab/main.py --demo 11
```

## Controls

- Drag a window to move it, or use **Super + left mouse drag**.
- Drag a terrain window's right edge to resize, or use **Super + right drag**.
- **Space:** walk / pause. **R:** reset. **N / P:** next / previous demo.
- **A:** create a bridge window in demo 1. **S:** split the bridge in demo 4.
- **Super + W:** close the red blocker. **Esc:** exit.

The HUD can also be dragged by its header. The transparent falling-character
rendering window stays protected and cannot take keyboard focus.

## Demos

1. Build a bridge: add a platform and move it into the gap.
2. Move the bridge: carry an existing platform between two ledges.
3. Widen the bridge: stretch the short platform across the gap.
4. Split the route: split a platform and position both pieces.
5. Ride the lift: board a platform, then carry it to the elevated exit.
6. Open the passage: close the red blocking window.
7. Hold the door: put the floating weight over the pressure pad.
8. Sticky mud: slows walking to 0.42×.
9. Fast lane: speeds walking to 1.8×.
10. Rolling hill: the man follows the grassy curve up and down.
11. Terrain mix: rearrange mud, a hill and a fast lane.

Edges connect within 22 logical pixels when the ground heights match. Walk off
an unsupported edge and he falls; a lower platform may catch him. R retries.
Terrain drawing and collision use the same profile in `experiments/surfaces.py`.
Falling sprites are also drawn inside terrain windows so they remain visible regardless of stacking. Landing checks sweep the path between frames to catch narrow platforms and slopes.

Moving a window carries its occupant, and his local walking position continues
to advance during dragging. There is no layout-settling pause.

## Visuals

The playground is now **Road to Omarchy**: drive a rally-style Quattro out of
Windows or Apple and reach the Omarchy wordmark. Press **B** to switch the
starting OS. The car has spinning wheels, suspension bounce, exhaust, hill lean,
and landing dust; it uses the same platform collision model. The Omarchy logo
asset comes from the installed `/usr/share/omarchy/logo.svg`.

Grass sways, mud bubbles and ripples, and water has layered waves. Colors follow
the active desktop palette. The earlier walking-man prototype retains its own
character.

## Requirements and scope

Omarchy/Hyprland Lua IPC, Python GTK3 and Cairo. No specific tiling layout is
required. The playground opens a fresh workspace, installs temporary window
rules, and removes them on exit. Installed desktop configuration is unchanged.

Use `--demo 11` for mixed terrain or `--demo 12` for water or `--state-file PATH` to export geometry and
state. Geometry is sampled every 60 ms; animation runs at 30 FPS. Physics tests
cover material speeds, hill profiles, handoffs, falls, landings and doors.

## Omarchy styling

The game reads the active `colors.toml` from Omarchy's state directory at launch
(with support for the older config location and a Kanagawa fallback). Text uses
the fontconfig monospace family, matching `omarchy font current`. Theme files are
read-only. Restart the game after changing desktop themes to load the new palette.

Design reference: https://omarchy.org/news/2026/09/omarchy-org-redesign-launches-with-29-languages/
Palette reference: https://omarchy.org/manual/making-your-own-theme/
Character reference: https://dev.37signals.com/assets/images/authors/dhh.png
The character is a stylized game caricature, not an official Omarchy asset.

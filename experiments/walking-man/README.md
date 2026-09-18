# Keep him alive — first level

Three real Hyprland tiles form a walking route on a newly allocated, empty
workspace: **Walker → Fire → Fixed goal**.

```sh
python experiments/walking-man/main.py
```

Requires Omarchy/Hyprland Lua IPC with dwindle, `preserve_split` and
`use_active_for_splits` enabled, plus Python GTK 3 and Cairo.

- **Space** or click the bottom instruction strip to start.
- Focus the walker and press **Super + Shift + Right** to swap it past the fire.
- **Super + Left / Right** changes focus, using the usual Omarchy bindings.
- **R** rebuilds the starting layout; **Esc** or closing any game window exits.

The walker travels with his tile, then enters the next tile on the right.
Walking into the fire loses. Reaching the door wins. The goal is kept in the
rightmost tile: swaps involving it are reversed on the next geometry poll.
Route windows moved out of the workspace or floated are returned to the tiled board.
The cloud remains floating.
Changing to a vertical layout pauses play; R restores the three-column layout.
Leaving the game workspace pauses the walker. Closing the game while viewing
it returns to the workspace you launched from.

Hyprland owns the layout and performs swaps through the existing Omarchy
shortcuts. No shortcuts are rebound and no installed configuration is edited.
The process installs one temporary window rule and removes it on exit.
This experiment is independent of rain/fire and DOOM.

Optional `--state-file /tmp/walking-man-tiled-state.json` exposes gameplay and
actual compositor geometry. Rendering runs at 30 FPS; geometry is polled at
10 Hz. A full room takes nine seconds to cross.

## Level two: rain rescue

After winning level one, **Space** (or clicking its result strip) advances to
level two. Launch it directly with:

```sh
python experiments/walking-man/main.py --level 2
```

The route stays **Walker → Fire → Goal**, as three full-height tiles.
The cloud is a fourth, **floating window**, initially over the left tile.
Start with **Space**, then drag the cloud over the fire window (plain left drag
or the usual Super+mouse gesture). Keep its bottom above the flames, with its
rain column covering them. Each flame section needs about three seconds of rain. Sweep the smaller cloud
across the fire: dry sections slowly regrow until the entire fire is out.
Complete extinction stays safe for that attempt. Flame height and percentage show progress. R restarts the level.

Swaps involving route windows are reversed in level two. The cloud is excluded
from the route and can be freely repositioned. Rain draws inside windows;
there is no overlay across desktop gaps.

## Walker handoff

The engine checks real route-window geometry at the right edge of the current
room. The walker transfers to the next tile on the same ground line, preserving
his remaining movement distance. Only that destination window draws him, and
keyboard focus follows him into it. The room title also identifies his current
tile. The empty starting tile no longer claims to contain the walker.

The cloud is a compact 320×220 floating window with no text or ground strip.
Its visible rain and hit detection share the same column beneath the cloud.

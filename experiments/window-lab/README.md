# Window interaction playground

Ten small interaction sketches for Keep Him Alive. Each uses two real floating
Hyprland windows. Drag the illustrated object into position relative to the
other window. A progress bar and result message show what the interaction does.
These are mechanic prototypes, not ten finished walking-man levels.

```sh
cd ~/Projects/hyprsplitter
python experiments/window-lab/main.py
```

**N / P** (or arrows) cycles demos. **1–9 / 0** selects one directly.
**R** resets both the state and window positions. **Esc** closes both windows.
The bottom previous/reset/next labels are clickable. Drag elsewhere in either
window, or use the normal Super+mouse gesture. Nothing starts on a timer:
interactions begin when the window positions match the hint.

| # | Interaction | What to do | Effect |
|---|---|---|---|
| 1 | Rain / Fire | Cloud above fire | Fire shrinks; dry fire regrows until fully out |
| 2 | Sun / Ice | Sun above ice | Ice melts to release a key; cool ice refreezes |
| 3 | Fan / Sailboat | Fan to the left, vertically aligned | Wind sails the boat to shore |
| 4 | Magnet / Key | Bring windows close | Pull the key across a gap |
| 5 | Rain / Seed | Cloud above seed | Water grows a climbing plant |
| 6 | Battery / Robot | Touch or overlap the window edges | Charge and wake a helper robot |
| 7 | Shield / Walker | Shield to the left, vertically aligned | Intercept three laser bursts |
| 8 | Trampoline / Walker | Trampoline below walker | Launch him to a high ledge |
| 9 | Weight / Drawbridge | Weight just above bridge (within 90 px) | Lower a bridge; it rises if released early |
| 10 | Lantern / Ghost | Bring windows close | Reveal and scare away a hidden ghost |

Successful demos latch their result until reset. Geometry checks are based on
real window edges and workspace membership, polled at 12.5 Hz. Animation runs
at 30 FPS; switching away pauses the simulation. The sketches depict results
inside the target window: e.g. the magnet moves the illustrated key, not the
whole target window. Shield progress demonstrates alignment, not a full combat
or health system. Effects do not create desktop overlays between the windows.

Requires Omarchy/Hyprland Lua IPC, Python GTK 3 and Cairo, like the other POCs.
It opens on a new empty workspace and restores the previous workspace when
closed from the playground. A process-scoped temporary rule makes the windows
float; no installed configuration or global shortcuts are changed.

Start a particular sketch with `--demo 8`. Optional
`--state-file /tmp/window-lab-state.json` exports state and real window geometry.

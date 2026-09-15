# Hyprsplitter

A spaceship flight school for **real Omarchy / Hyprland shortcuts**.
Each lesson is a separate small game with one objective and its own board.
The windows really move, rotate, resize, float, fullscreen, and close.

```sh
./play
./play --lesson lasers
./play --lesson shoot
```

Press **Space** to start. Finish a lesson, then press Space for the next one.
**R** retries the current lesson; **1–7** jumps to a lesson; **Escape** quits.
Super means the Windows key. Your normal desktop bindings remain active.

## Flight school

| Phase | Game | Task |
| --- | --- | --- |
| 1 | Asteroid field | Super+Shift+arrows moves the ship through all 24 tiles (6 × 4). Dodge 12 impacts. Overlapping bursts arrive every 1.2–2 seconds, with solo rocks and clusters of up to 6. Each rock gets a 2.6-second countdown; at most 10 sectors are threatened at once. |
| 2 | Laser gates | Only 2 windows. Super+J rotates the split; Super+Shift+arrows swaps sides. Move to the marked safe half for 4 gates. |
| 3 | Target practice | Super+arrows selects a red enemy. Super+W closes that actual window and destroys the ship. Close 3 enemies; keep your cyan ship. |
| 4 | Docking | Super+T undocks. Super+left-drag moves the ship's center onto the beacon. Super+T lands again. |
| 5 | Cargo bay | Super+minus/equals changes width. Reach 120%, then restore 100%. |
| 6 | Deep space scan | Toggle fullscreen, then toggle back to tiling. |
| 7 | Panorama | Toggle maximize, then return to tiling. |

The game displays the next action needed, progress, and a completion screen.
Mistakes give feedback and another attempt. Closing the wrong tile restores the
current exercise with an explanation. Selecting a window alone never destroys it.
There is no auto-fire, health, energy, boss, or combined survival mode.

Fullscreen, maximize, float, split, and close hints are read from installed
binding descriptions. On this development machine, **Super+Alt+F is fullscreen**
and **Super+F is maximize**. Stock Omarchy uses the reverse assignment.
Native actions work even if their shortcuts are customized.

## Requirements

- A running Hyprland session with the Lua dispatcher API (tested on 0.56.2)
- Dwindle layout with `preserve_split` and `use_active_for_splits` enabled
- Python 3, PyGObject, GTK 3, and Cairo

A board opens on the first unused workspace starting at 90. Only a temporary
rule matching this process's windows is installed. It is disabled on exit;
no desktop configuration files or global keybindings are changed. Switching
away pauses progress. Escape closes the board and restores the previous focus
when exiting from the lesson workspace.

## Development

```sh
python -m unittest -v
./play --smoke-test
```

Unit tests cover isolated lesson objectives, timing, retry behavior, and native
geometry interpretation. The live smoke test exercises real swaps, split
rotation, focus, enemy closes, docking, resizing, fullscreen, maximize, and
recovery after accidentally closing the friendly ship.

Previous combat prototypes remain available in Git tags through `v0.3.2`.

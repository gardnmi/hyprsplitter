# Hyprsplitter

A spaceship game played with **nine real Hyprland tiled windows**. Your ship is
one persistent window: steering swaps that window with a neighboring sector.

## Play

```sh
./play
```

The game opens on the first unused workspace starting at 90. Press **Space** to
launch. Red sectors warn before lasers fire; amber sectors warn of asteroid
impacts. Move into a clear sector before the countdown expires. Survive waves
for points. Three hits end the run.

The opening is deliberately hard for recording: **six dangerous sectors from
wave one**, a **0.95-second warning** shrinking to 0.65 seconds, and only a
0.12-second breather after each impact. Every wave targets your current sector,
so you must keep moving. Three safe sectors remain, with an escape always
within two swaps when the warning begins.

| Key | Action |
| --- | --- |
| Arrows / WASD | Swap the ship window with an adjacent tile |
| Space / Enter | Start or pause |
| R | Reset to the launch screen |
| Escape / Q | Close all game windows |

Controls work from any game tile. Switching away pauses the simulation
automatically. Closing any tile ends the whole game. Normal exit restores your
previous workspace when you are still on the game workspace.

## Requirements

- Hyprland with the Lua dispatcher API (tested against 0.56.2).
- Dwindle layout with `preserve_split` and `use_active_for_splits` enabled.
- System Python, GTK 3, PyGObject and pycairo. These are already installed on
  the development machine. The launcher uses system Python to find GI bindings.

No persistent desktop configuration is edited. A temporary, process-specific
window rule routes the game windows and is disabled on exit. No global bindings
are installed. A forced kill may leave an inert rule for that process until the
next Hyprland config reload.

## Prototype limits

Hazards resolve against logical sectors when the warning timer expires; they
are drawn inside each window. Movement uses native tiling swaps with your
Hyprland window animations, so the ship glides between sectors. Collision uses
the destination sector as soon as a swap is issued. Don't add other apps to the game workspace or rearrange its split
tree while playing. Floating/moving a tile off the board ends the session.

## Checks

```sh
python -m unittest -v
./play --smoke-test
```

The smoke test temporarily opens the real board, verifies eight native swaps
and the grid geometry, then closes it and restores the previous workspace.

## Source

- `game.py`: wave timing, hazards, shields, score and board navigation.
- `hyprsplitter.py`: GTK windows, native Hyprland IPC, input and lifecycle.
- `render.py`: Cairo vector artwork, HUD and effects.

API references: [Hyprland dispatchers](https://github.com/hyprwm/hyprland-wiki/blob/main/content/configuring/core/dispatchers.md),
[Dwindle layout](https://github.com/hyprwm/hyprland-wiki/blob/main/content/configuring/layouts/dwindle-layout.md),
[window rules](https://github.com/hyprwm/hyprland-wiki/blob/main/content/configuring/core/rules/window-rules.md).

# Clear Tetris

A quiet falling-block game in a transparent floating window. Keep a meeting or
video visible through the empty board. No sound, external artwork, or extra
dependencies beyond the repository's GTK3/Cairo setup.

```sh
python games/clear-tetris/main.py
```

It also appears as **CLEAR TETRIS** when you next launch `./arcade`.
The window opens near the upper-right corner of the current monitor, on the
current workspace, and starts paused. Click **RESUME** or focus the board and
press **P**. Drag the header to move it. Smaller monitors get a scaled board.

| Control | Action |
| --- | --- |
| Left / Right | Move (hold to repeat) |
| Down | Soft drop |
| Up / X | Rotate clockwise |
| Z | Rotate counterclockwise |
| Space | Hard drop |
| C / Shift | Hold piece, once per drop |
| P / Enter | Pause / resume |
| T | Cycle clear / 12% / 28% / 48% dark board tint |
| G | Toggle the faint grid |
| R | New game, initially paused |
| Escape / header X | Exit |

The outline at the bottom previews the landing position. Clear full rows to
score; every ten rows increases the level. Pieces have a half-second lock delay
and simple wall/floor kicks. This is a small Tetris-style game, not a full
implementation of competitive rotation/scoring rules.

Switching focus to Zoom or another app automatically pauses the game. Resume
explicitly when you return. The transparent rectangle accepts mouse input;
click outside it to interact with the meeting, or move the board out of the way.
Keyboard controls work while the game has focus; no global shortcuts are installed.

Use Zoom windowed or maximized. A compositor's true fullscreen mode can cover
floating windows. The game requests above-window stacking, but the compositor
decides the final order. It does not alter Zoom or desktop configuration.
It can appear in a whole-screen share; share the meeting/app window if you want
to exclude other desktop windows.

Unlike cartridges that use a dedicated workspace, this overlay intentionally
stays on your current workspace. It uses a temporary rule scoped to its unique
window title to disable the border, shadow, and blur; the rule is removed on
normal exit, SIGINT, or SIGTERM. Simulation and redraws stop while paused or
off-workspace.

```sh
python -m unittest discover -s games/clear-tetris -p 'test_*.py'
```

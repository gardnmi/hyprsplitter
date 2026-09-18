# Road to OMACON

A window-to-window puzzle starring **one Linux penguin, Tux**.
The folder and some internal variables retain the earlier "lemur" prototype name.

```sh
python experiments/lemur-falls/main.py
# Or insert ROAD TO OMACON in ./arcade.
```

## Route

1. Place the paired portals to divert minigun fire away from Tux's fall.
   Bullets enter one portal and exit the other; Tux can teleport too.
2. Tux leaves the fixed source window and drops into the green Omarchy chamber.
   Drag/scroll the symbol to rotate its opening and release him toward the left.
3. Tux rides an office chair down the Windows hillside, smashes its logo, and
   flies toward the elevator. Departure triggers a playful blue screen.
4. Dock the calendar and coffee icon windows into the matching lift slots.
   One icon raises the carriage halfway; both raise it to the Apple crossing.
5. Redirect portal fire into the Apple brick barrier to break it. Keep the
   outgoing bullets away from Tux. He belly-slides across the Apple scene.
6. Reach the OMACON window at the top right to trigger its bright neon celebration.

The source, minigun strip, chamber position, Windows/Apple scenes, elevator
shaft, and destination are fixed. Portals and plugin icons are movable.
The calendar/coffee icons are game pieces; they do not control real desktop plugins.

## Controls and details

- **Space** or click source: start/pause.
- **R**: reset the attempt, scene effects, portals, and plugin positions.
- **Escape**: exit.
- Drag movable windows with the mouse or normal Hyprland floating-window controls.
- Drag/scroll the green chamber to rotate it.

Windows has moving clouds, rolling hills, and a tumbling office chair.
Apple has a rainbow beach ball, mismatched rounded corners, a “Think different.”
reveal, and title-bar buttons that fall off on departure. Gunfire produces
short-lived cartoon blood effects. Other applications are not platforms.

## Implementation

GTK3 owns interactive windows; a separate GTK4 layer-shell process draws fixed
scenes. The parent exchanges state with that helper in a private temporary
directory, and stops it on exit. Fixed layers sit below normal windows so movable
pieces remain accessible. A separate overlay renders airborne Tux.

The installed ttfx program animates the source wordmark. Requires GTK3, GTK4,
gtk4-layer-shell, Cairo, PyGObject, ttfx, and Omarchy's Symbols Nerd Font.
Artwork provenance is listed in [ASSETS.md](../../docs/ASSETS.md).

Tests: `python -m unittest discover -s experiments/lemur-falls -p 'test_*.py'`.
Layout is in `layout.py`; simulation is split between `model.py`, `mechanics.py`,
`portals.py`, `catcher.py`, and `barrier.py`.

# Adding a game

## Files

```text
games/my-game/
  game.json       # cartridge metadata, discovered on launcher startup
  main.py         # executable game and native-window lifecycle
  model.py        # simulation/geometry, independent of GTK
  test_model.py   # isolated behavior tests
  README.md       # controls, objective, requirements
  assets/         # optional; document provenance
```

Use `python tools/new_game.py my-game --title "MY GAME"` to generate this
structure from `templates/window-game/`. The initial example asks the player
to drag the small window entirely inside a larger dock. It includes reset,
workspace visibility checks, scoped rules, and shutdown handling.

## Cartridge manifest

```json
{
  "id": "my-game",
  "title": "MY GAME",
  "subtitle": "A COMMUNITY WINDOW GAME",
  "accent": "cyan",
  "entry": "main.py"
}
```

- **id:** unique lowercase letters/digits/hyphens, starts with a letter, at most
  32 characters. `console` is reserved.
- **title:** up to 20 characters; printed on the cartridge.
- **subtitle:** up to 48 characters; descriptive metadata.
- **accent:** `cyan`, `orange`, `blue`, `bright_green`, `red`, `yellow`, or `green`.
- **entry:** Python file relative to this manifest, inside the repository.

Bundled games use `experiments/console/games.json`; their entry paths are relative
to the repository root. Community manifests are discovered in sorted directory
order after those games. Duplicate IDs or invalid paths fail with a manifest
error before any windows open.

Discovery reads JSON only. Launching a cartridge executes local Python with the
user's permissions; this is a contribution format, **not a sandbox or online
plugin installer**. There is no automatic download or install step.

The console numbers cartridges automatically and wraps them into rows as the
collection grows. Optional bespoke cartridge art can be added to
`experiments/console/art.py:illustration`; unknown IDs get a generic animation.

## Lifecycle contract

The launcher starts `[sys.executable, entry]` with the repository root as working
directory and `GDK_BACKEND=wayland`. It captures stdout/stderr in a per-game log.
The launcher waits for that process to exit before restoring the cartridge.
Keep the main process alive while playing; do not daemonize.

A game must:

1. Find a free workspace, remember the previous one, and create only its own
   uniquely titled windows.
2. Scope temporary rules to its process's titles. Do not change global bindings,
   theme settings, existing windows, or configuration files.
3. Pause simulation/redraws when hidden. Clamp time steps after delays.
4. Handle Escape, native window close, SIGTERM, and SIGINT. Closing any mandatory
   scene window should exit the game, not endlessly recreate it.
5. Stop timers, terminate/wait for owned child processes, destroy windows, and
   disable temporary rules during cleanup. Make cleanup safe to call twice.
6. Restore the prior workspace only if the player is still on the game's workspace.
7. Return zero for a normal exit and nonzero for a startup failure.

If you add a helper subprocess, use a private temporary directory for IPC;
clean it up after waiting for the helper to exit. GTK3 and GTK4 must stay in
separate processes, as in Road to OMACON.

## Coordinates and input

Hyprland client positions and sizes describe logical desktop coordinates.
Monitor width/height must be divided by scale; include the monitor x/y offset.
Keep physics in one coordinate system and map it explicitly to each canvas.
Visual tilt does not rotate a native rectangular Wayland surface.

If entities cross windows, use swept collision tests to avoid tunneling.
Decide which surface renders each entity and test foreground/background stacking.

Route firing and key events through every interactive surface. A transfer of
focus between two game windows is not the same as leaving the game.
Only make decorative surfaces click-through; an input overlay needs to receive
the first click even when the main window is not focused.

## Where to learn from existing games

- `templates/window-game/`: smallest complete lifecycle and interaction example.
- `experiments/quattro-jump/model.py`: ballistic movement across scene windows.
- `experiments/omarchy-wars/board.py`: desktop-coordinate collision and transport.
- `experiments/lemur-falls/`: GTK3 input windows plus a GTK4 layer-shell helper.
- `experiments/theme.py`: read-only installed palette with fallback colors.

These are reference implementations, not a stable shared game-engine API.
Prefer extracting a shared helper only once multiple games actually need it.

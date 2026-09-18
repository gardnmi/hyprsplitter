# Omatari · Hyprsplitter

**Minigames played with real desktop windows, built for Omarchy.**

Omatari is the cartridge console for this collection. Drag a floating cartridge
into its slot, click to seat it, and play. Close the game to return to the console.
The desktop is part of the game: windows become ramps, portals, platforms,
enemies, and puzzle pieces.

This is an early, Omarchy-only release. It uses Python, GTK, Cairo, and Hyprland's
Lua IPC API, tested on Hyprland **0.56.2**. Standalone Hyprland, other compositors,
and Windows/macOS are not supported.

## Setup

From a terminal in an active Omarchy desktop session:

```sh
omarchy pkg add git python python-gobject python-cairo gtk3 gtk4 gtk4-layer-shell ttfx
git clone https://github.com/gardnmi/hyprsplitter.git
cd hyprsplitter
python tools/doctor.py
./arcade
```

Run as your normal user. No pip install or virtual environment is needed;
`arcade` and `play` use system Python. Python **3.11+** is required.
GTK4, gtk4-layer-shell, and ttfx are used by Road to OMACON; other cartridges use
GTK3/Cairo. Road to OMACON's icon artwork also uses Omarchy's Symbols Nerd Font.

The dependency check is read-only. Games use their own workspaces and temporary,
process-scoped window rules. They do not rewrite desktop configuration or global
keybindings. Games pause simulation or rendering when their workspace is hidden.

## Games

| Cartridge | What you do | Guide |
| --- | --- | --- |
| Flight School | Learn real window shortcuts through six spaceship lessons | [Controls and lessons](docs/FLIGHT_SCHOOL.md) |
| Chase the Sun | Charge a Quattro, adjust its ramp, and jump through three sunset windows | [Quattro](experiments/quattro-jump/README.md) |
| Road to OMACON | Help Tux through redirected gunfire, a rotating chamber, a chair crash, and a plugin lift | [Tux puzzle](experiments/lemur-falls/README.md) |
| Zero Day | Finish a fictional install, then defend against waves of satirical enemy windows | [Zero Day](experiments/omarchy-wars/README.md) |

In the console, drag a cartridge's contacts onto the slot, wait for alignment,
then click it. **R** resets the console layout; **Escape** exits.
In games, Escape exits and R retries/resets. See each guide for other controls.
Native **Super+W** closes a game; Flight School's target-practice lesson uses it
to destroy enemy windows, so close the player's cyan ship to exit that lesson.

Zero Day contains flashing combat effects; Road to OMACON contains cartoon
blood effects. Chase the Sun is an interactive toy with visual surprises.

### Launch directly

```sh
./play
python experiments/quattro-jump/main.py
python experiments/lemur-falls/main.py
python experiments/omarchy-wars/main.py
```

Flight School additionally requires dwindle with `preserve_split` and
`use_active_for_splits` enabled. The doctor reports these requirements separately.

### Update

Close the games, then:

```sh
git pull --ff-only
python tools/doctor.py
./arcade
```

## Make your own cartridge

```sh
python tools/new_game.py my-game --title "MY GAME"
python games/my-game/main.py
./arcade
```

The generated example is already a playable two-window docking game. Omatari
discovers its JSON manifest automatically, supplies generic cartridge art, and
lays out the extra cartridge. No launcher source edits are required.

Start with [CONTRIBUTING.md](CONTRIBUTING.md), then read
[Adding a game](docs/ADDING_A_GAME.md). Contributions of small mechanics, artwork,
tests, bug fixes, and documentation are welcome.

## Development

```sh
python tools/test.py
python tools/test.py --labs
```

Tests run separately for each game to isolate same-named Python modules. CI runs
these tests without launching desktop windows. Native interactions still need
manual testing on Omarchy. See the [release checklist](docs/RELEASE.md).

### Repository map

- `arcade`, `experiments/console/`: Omatari launcher, catalog, and cartridge art.
- Root Python files: original Flight School.
- `experiments/quattro-jump/`, `lemur-falls/`, `omarchy-wars/`: bundled games.
- `experiments/theme.py`, `rally.py`, `surfaces.py`, `visuals.py`: shared drawing helpers.
- `games/`: new community cartridges.
- `templates/window-game/`: runnable starter.
- `tools/`: dependency check, scaffold generator, isolated test runner.
- Other experiments: development references, not supported cartridges.
  `experiments/pixel-doom/` is a separate stress test requiring custom builds;
  its generated output is ignored.

## Troubleshooting

Run `python tools/doctor.py` first. Use the system Python if `gi` or `cairo`
cannot be imported. A live Omarchy session and the Lua IPC API are required;
passing unit tests on another OS does not mean the games can run there.

Launcher logs and per-cartridge output are in `~/.cache/hyprsplitter/`
(or `$XDG_CACHE_HOME/hyprsplitter/`). Zero Day stores its best score under
`~/.local/state/hyprsplitter/` (or `$XDG_STATE_HOME/hyprsplitter/`).

For issues, include reproduction steps, game name, version information,
monitor resolution/scale, and relevant logs. A short recording helps diagnose
window-stacking or pointer-focus problems.

## License and credits

Project code is licensed under the [MIT License](LICENSE).
See [asset provenance](docs/ASSETS.md) for artwork and redistribution status.
Omatari is an independent project; referenced brands do not imply endorsement.

### Flight School preview

![Flight School gameplay](docs/gameplay.gif)

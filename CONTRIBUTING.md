# Contributing to Omatari

Omatari is the game console; Hyprsplitter is the repository and original Flight
School game. Contributions can be games, mechanics, artwork, fixes, tests, or
documentation. The supported desktop is **Omarchy with Hyprland's Lua API**,
tested on 0.56.2. This is an early release, not a cross-desktop game engine.

## Get started

1. Follow the [setup instructions](README.md#setup).
2. Run `python tools/doctor.py` to check your local dependencies.
3. Run `python tools/test.py` before making changes.
4. Make a branch for one focused change.

No pip installation is needed. Use system Python; a virtual environment often
cannot see the distribution's PyGObject packages.

## Add your first game

```sh
python tools/new_game.py my-game --title "MY GAME"
python games/my-game/main.py
python -m unittest discover -s games/my-game -p 'test_*.py'
./arcade
```

The scaffold creates a playable two-window docking example, a pure model, tests,
a README, and a manifest. Relaunch Omatari to discover the new cartridge.
No launcher edits are needed. Generic animated cartridge art is provided.

Read [Adding a game](docs/ADDING_A_GAME.md) for the manifest and lifecycle contract.
Existing games remain under `experiments/` to avoid breaking launch commands;
new contributions belong under `games/<slug>/`.

## Code conventions

- Use four-space indentation, descriptive names, and small functions in new code.
  Older prototypes are compact; avoid unrelated whole-file reformatting in a fix.
- Keep simulation rules in `model.py` (or similarly named modules) without GTK,
  filesystem, or compositor side effects. Use seeded randomness for tests.
- Keep drawing and desktop integration separate from collision and timing rules.
- Use `experiments.theme.rgb()` for palette colors when practical.
- Resolve assets relative to `__file__`, not the current directory or a personal path.
- Bound entity counts, particles, timers, and subprocesses. Pause work off-workspace.
- Keep changes scoped to the game. Never rewrite a player's desktop configuration.
- Prefer code-drawn artwork. Include source, author, license, and modifications
  for any added assets; do not assume an image found online is redistributable.

## Tests

```sh
python tools/test.py
python tools/test.py --labs
```

Each suite runs in its own process: several games have modules named `model`
and `art`. Combining all suites in one Python interpreter can test the wrong
module. The default runner includes new `games/*/test_*.py` suites automatically.

CI runs the tests without an active Hyprland session. It cannot establish whether
native window stacking, pointer focus, monitor scaling, and cleanup work.
For a gameplay or integration change, also check on Omarchy:

- Launch directly and via its cartridge.
- Test mouse and keyboard input in every interactive window.
- Move/resize supported pieces; try an offset/scaled monitor if available.
- Leave the workspace and return; reset the game.
- Exit via Escape and Super+W. Verify all owned windows and helper processes exit.
- Return to Omatari, launch again, then close Omatari while the game runs.

`python tools/smoke.py` opens the launcher, each bundled game, and the starter
for four seconds each, then checks shutdown and workspace restoration. Do not
interact with the desktop during that check. It does not play through levels.

Flight School additionally has `./play --smoke-test`. It opens and manipulates
real windows, so run it deliberately in a live desktop session.

## Pull requests

Explain the problem, what changes for the player, and how you tested it.
Include a short clip for visual or interaction changes. Mention dependencies,
controls, known limitations, and any assets with separate licenses.
Use the PR template. A small playable mechanic is easier to review than a new
engine abstraction with no game using it.

Do not commit recordings, local caches, benchmark output, or generated binaries.
The large Pixel DOOM experiment is outside the supported cartridge/test workflow.

## Reporting issues

Include the game, steps to reproduce, expected/actual behavior, Omarchy/Hyprland
versions, monitor scale, and whether you launched directly or through Omatari.
Run `python tools/doctor.py`. Launcher and game logs are in
`$XDG_CACHE_HOME/hyprsplitter/` (normally `~/.cache/hyprsplitter/`).
Review logs and recordings for personal information before attaching them.

## Licensing

Project code is licensed under the [MIT License](LICENSE). By submitting code
for inclusion, you agree to license your contribution under the same terms.
Only submit work you have the right to contribute. Third-party assets retain
their own terms; include their attribution and license information. See
[asset provenance](docs/ASSETS.md) and [release readiness](docs/RELEASE.md).

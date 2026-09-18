# Release checklist

## Before publishing

- [x] Add the [MIT License](../LICENSE) and document contribution terms.
- [ ] Resolve the artwork permissions listed in [ASSETS.md](ASSETS.md).
- [ ] Run `python tools/doctor.py` on a clean Omarchy checkout.
- [ ] Run `python tools/test.py --labs`.
- [ ] Run `python tools/smoke.py` in an idle desktop session.
- [ ] Complete the live checks in [CONTRIBUTING.md](../CONTRIBUTING.md) for all
      four bundled games and the generated template.
- [ ] Check more than one monitor size/scale; record known limitations.
- [ ] Confirm a clean clone includes both required PNG assets and executable
      `arcade`/`play` scripts.
- [ ] Review `git status --short` and staged files. The games began as untracked
      experiments: ensure their source/assets are included intentionally.
- [ ] Exclude promotional videos, raw recordings, benchmark output, caches, and local build products.
- [ ] Review final diff, tag the release, and write tested versions/known issues.

Unit tests and headless rendering do not replace testing real Hyprland surfaces.
The bundled games depend on the Lua dispatcher API; older Hyprland builds using
only legacy dispatchers are not supported. Ubuntu CI checks Python behavior,
not desktop compatibility.

## Scope

Supported collection: Omatari console, Flight School, Chase the Sun, Road to
OMACON, and Zero Day. New community games use `games/*/game.json`.

Rain/fire, walking-man, window-lab, and platform-lab are development references.
Pixel DOOM is a separate stress experiment with locally built compositors,
terminals, recording tools, and external DOOM data. It is not a playable
cartridge, not run by standard CI, and not a supported installation path.

## Release contents and state

No installer modifies a desktop config or downloads games. Players clone the
repository and run the shell entry points as their ordinary user.

Launcher logs: `$XDG_CACHE_HOME/hyprsplitter/`.
Zero Day best score: `$XDG_STATE_HOME/hyprsplitter/zero-day.json`.
Both default to the corresponding `~/.cache` / `~/.local/state` directories.

## Local validation — 2026-09-17

- 134 unit tests passed with `python tools/test.py --labs`.
- `python tools/doctor.py` passed on the development Omarchy installation.
- Launcher, four bundled games, and starter mapped native windows, exited
  cleanly on SIGTERM, and restored the previous workspace.
- A freshly generated community cartridge was discovered and passed the same
  live startup/shutdown check; the temporary example was removed afterward.
- Python source parsing and local links in public guides passed.
- Full playthroughs, other monitor configurations, and a separate clean-machine
  installation remain release checks. The CI workflow has been added but has
  not yet run on GitHub.
- No release tag, commit, push, or publication was performed during preparation.

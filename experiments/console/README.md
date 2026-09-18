# Omatari

From the repository root:

```sh
./arcade
```

Omatari is an Omarchy-themed video game system with ribbed black plastic, metal
switches, and a woodgrain front. Its console and floating cartridges open
on a free workspace. Drag a
cartridge's gold contacts onto the glowing slot and let it snap into alignment. Click the cartridge to press it home: it depresses,
rebounds, and slides into the slot before the corresponding game opens on its own
workspace. Escape from the game returns to the console. Only one game launches
at a time.

- Flight School: the original six space lessons.
- Chase the Sun: the three-window Quattro jump.
- Zero Day: the Omarchy install-defense arena shooter.
- Road to OMACON: Tux's window puzzle.

Drag directly or use normal Hyprland floating-window shortcuts. **R** or the
console's RESET button restores the starting layout. **Escape** closes the launcher; POWER shows the quit shortcut. Closing the launcher also asks its running game to exit.

Uses the installed Omarchy palette, GTK3 and Cairo. Temporary window rules are
removed on exit; no desktop configuration is changed. Game launch errors are
logged under `~/.cache/hyprsplitter/` (or `$XDG_CACHE_HOME/hyprsplitter/`).

Checks: `python -m unittest discover -s experiments/console -p 'test_*.py'`.

## Contributing cartridges

Run `python tools/new_game.py my-game --title "MY GAME"` from the repository root.
The console reads bundled entries from `games.json` and discovers additional
`games/*/game.json` manifests when it starts. Cartridge numbering, generic art,
and multi-row layout work without per-game launcher edits.
See [Adding a game](../../docs/ADDING_A_GAME.md).

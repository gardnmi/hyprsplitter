# Hyprsplitter

A spaceship game played with **real Hyprland windows**. Dodge laser lanes by
swapping your ship's tile, shoot across the layout, and fight a boss that
breaks into separate windows. Grow, split, float, or fullscreen your ship.

## Play

```sh
./play
./play --boss   # Start directly with the Window Devourer, useful for recording
```

The game opens on the first unused workspace starting at 90. **Space** launches
the game. Controls work from any game window; your ship stays the same actual
window as you maneuver. Movement uses your normal Hyprland animations.

| Key | Action |
| --- | --- |
| Arrows / WASD | Move the selected ship: swap tiles, or steer during free flight |
| I / J / K / L | Shoot up / left / down / right; hold to keep firing |
| G | Grow into a larger gunship: double damage for 5 seconds; 25 energy |
| E | Split off a second ship window; 30 energy. Press again to merge for free |
| Tab | Switch control between the two ships |
| F | Float the primary ship for 3 seconds; 35 energy. Press again to land early |
| X | Fullscreen nova: briefly fullscreen the primary ship and hit every enemy; 100 energy |
| Space / Enter | Start or pause |
| R | Reset the run and restore the board |
| Escape / Q | Close the entire game |

### Survival and shooting

The opening is deliberately hard: six of the nine screen sectors are targeted
from wave one, with a 0.95-second warning shrinking to 0.65 seconds. Red means
laser lock; amber means incoming asteroids. You have three shared shields.
Lasers strike together. Asteroids have individual countdowns and land one at a
time, with randomized 0.18–0.34 second gaps. A cleared sector becomes safe while
other asteroids are still inbound.

Shoot along a clear horizontal or vertical line through the physical layout.
Shots hit the first enemy in that direction. Enemy windows block movement;
empty tiles can be swapped. Both ships fire while split, but either can take a
hit. Flying protects the primary ship from sector attacks; the wing remains
vulnerable. Energy regenerates over time, with a bonus for destroying enemies.

### The Window Devourer

The boss arrives on wave five, or immediately with `--boss`:

1. **Armored window:** a large tile squeezes the battlefield. Destroy its 18 HP.
2. **Fracture:** its tile splits into three independently targetable windows,
   each with 6 HP.
3. **Detached core:** the fragments merge into a 12 HP floating boss that moves
   across the top of the arena. Line up shots and finish it for victory.

All abilities affect actual compositor windows. Formations rebuild their tiling
tree when needed, keeping surviving ship windows alive. Merging and landing
restore the tiled formation. Fullscreen nova returns to the previous window mode.

## Requirements

- Hyprland with the Lua dispatcher API (**tested on 0.56.2**).
- Dwindle layout with `preserve_split` and `use_active_for_splits` enabled.
- Python 3.12+, GTK 3, PyGObject and pycairo.
- The launcher uses `/usr/bin/python` so it can find system GI bindings.

No persistent desktop configuration is edited and no global bindings are
installed. A process-specific window rule is disabled on normal exit. Closing
any game tile ends the entire session. Switching away pauses gameplay; exiting
from the game workspace returns you to your previous workspace. A forced kill
can leave an inert process-specific rule until the next Hyprland config reload.

## Prototype boundaries

- This is a compositor experiment targeting the tested Hyprland version.
- Don't introduce other apps into the game workspace or manually change its
  tiling tree while playing. Moving a tile off the board ends the session.
- The screen is divided into nine hazard sectors. A window's center determines
  its sector after resizing. Collision uses destination geometry during native
  movement animations. Projectiles are drawn inside windows; they are not
  separate desktop windows.
- Growth currently costs energy and resizes the ship; it does not absorb kills.
  Floating provides timed evasion with keyboard steering. These are first-pass
  abilities, with further balancing expected.

## Validation

```sh
python -m unittest -v
./play --smoke-test
./play --combat-smoke-test
```

The first live test checks eight real window swaps. The combat test checks
shooting, growth, wing deployment/movement/merging, flight/landing, fullscreen,
every boss transition, persistent ship identity and board restoration. Both
temporarily open their own game workspace and close it afterward. Run live
tests one at a time and keep their workspace focused.

## Versions

- [`v0.1.0`](https://github.com/gardnmi/hyprsplitter/tree/v0.1.0): the original
  hard-mode dodge prototype, preserved before combat development.
- Current: shooting, three-stage boss and native window abilities.

## Source

- `game.py`: combat, hazards, energy, abilities and boss state.
- `combat.py`: physical navigation and firing lanes.
- `hyprsplitter.py`: GTK windows, Hyprland IPC, input and lifecycle.
- `render.py`: procedural Cairo vector artwork and HUD.

API references: [Hyprland dispatchers](https://github.com/hyprwm/hyprland-wiki/blob/main/content/configuring/core/dispatchers.md),
[Dwindle layout](https://github.com/hyprwm/hyprland-wiki/blob/main/content/configuring/layouts/dwindle-layout.md),
[window rules](https://github.com/hyprwm/hyprland-wiki/blob/main/content/configuring/core/rules/window-rules.md).

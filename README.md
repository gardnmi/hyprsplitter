# Hyprsplitter

Learn **Omarchy / Hyprland shortcuts** by piloting a real desktop window.
The game observes native compositor actions: your normal shortcuts move,
resize, float and fullscreen the ship. It does not install replacement bindings.

## Start training

```sh
./play
./play --lesson shoot   # Revisit the shooting lesson directly
```

A dedicated workspace opens, starting at the first unused number from 90.
Press **Space** when ready. The default mode introduces one mechanic at a time,
with three practice waves per lesson. Each new lesson stops on an explanation
card until you press Space. Earlier mechanics gradually return in later lessons.

| Lesson | What you practice |
| --- | --- |
| 1 | Focus the ship and swap windows; one slow laser lane, no enemies |
| 2 | React to random asteroid arrivals: a mix of solo rocks and small groups |
| 3 | Learn to shoot up at one target, without incoming hazards or a time limit |
| 4 | Toggle floating and drag the ship, then return to tiling |
| 5 | Resize the ship for a temporary double-damage bonus |
| 6 | Deploy a wing, change split orientation, and focus either ship |
| 7 | Learn the difference between fullscreen and maximize |
| 8 | Combine the mechanics against the Window Devourer |

Opening laser warnings last **3.2 seconds**, with a **1.2-second breather** between
waves. Later lessons speed up gradually. The boss does not arrive until lesson 8.

## Real desktop controls

Use your installed shortcuts. These are the stock Omarchy bindings:

| Shortcut | Desktop action / game effect |
| --- | --- |
| Super + arrows | Focus an adjacent window; focus your ship before maneuvering |
| Super + Shift + arrows | Swap the focused window in that direction |
| Super + T | Toggle floating / tiling; floating gives 3 seconds of evasion |
| Super + left-drag | Move a floating window |
| Super + right-drag | Resize a window |
| Super + minus / equals | Resize horizontally; Shift changes height |
| Super + J | Rotate an existing split between horizontal and vertical |
| Super + F | Fullscreen; activates a brief nova |
| Super + Alt + F | Maximize / full width |
| Super + W | Close the game window and end the session |

**Super is the Windows key.** The game reads binding descriptions at startup to
label fullscreen, maximize, floating, split rotation and close actions. For
example, the development machine swaps the stock fullscreen/maximize shortcuts:
its hints show **Super+Alt+F** for fullscreen and **Super+F** for maximize.
Unrecognized custom bindings still work natively, but may require a manual hint
update. Your configured Super+arrows focus shortcuts also work normally.

The only game-specific keys are **Space / Enter** to start, continue or pause,
**R** to restart, and **Escape / Q** to exit. Old WASD/IJKL and ability-letter
controls are removed. Your ship **always shoots up**, automatically hitting the
first enemy above it in the same firing lane. Move below the target and align
horizontally. The ship shows an upward guide and tells you which way to move;
the target gains a cyan lock outline, flashes on hits, and displays remaining HP.
The shooting lesson waits for three target kills before adding hazards back in.

**Enemy tiles are unsafe to enter.** They keep a red border and a
`HOSTILE / TOUCH = -1 SHIELD` warning even when target-locked. Swapping your ship
into a live enemy costs one shield and bounces the ship back. Floating contact
also hurts. Focusing a window is safe. Destroying an enemy clears its tile,
awards 250 points and repairs one shield (up to three), with visible feedback.

**Deploying a wing is a game button**, unlocked in lesson 6, costing 30 energy.
Click it again to merge. Super+J is correctly taught as split orientation;
it does not create windows. Focus either ship with the real focus shortcuts.

Native window changes persist as desktop actions. A resize grants five seconds
of stronger shots. Floating evasion lasts three seconds; remain floating or
land using your real toggle. Fullscreen nova exits fullscreen after its effect
(or toggle it off yourself). Formation changes and restart may rebuild the
game's tiling tree while keeping surviving ship windows alive.

## Boss and arcade practice

```sh
./play --boss     # Jump straight to the boss, skipping lessons
./play --arcade   # Original fast difficulty, without instruction pauses
```

The Window Devourer has an enlarged armored tile (18 HP), breaks into three
separate windows (6 HP each), then becomes a moving floating core (12 HP).
Destroy the core for victory. Split ships share three shields; either may take
a hit. Laser volleys fire together. Asteroids appear at random times, sometimes
alone and sometimes in groups of two or three that impact together. Future
arrivals stay hidden until their warning begins; every rock gets a full warning.

## Requirements and behavior

- Hyprland with the Lua dispatcher API, tested on **0.56.2**.
- Dwindle layout with `preserve_split` and `use_active_for_splits` enabled.
- Python 3.12+, GTK 3, PyGObject and pycairo. The launcher uses system Python.

No persistent desktop configuration is edited, and no global bindings are
installed or intercepted. A process-specific window rule is disabled on exit.
Switching away pauses gameplay. Closing any game window ends the session.
Exiting from the game workspace returns to your previous workspace.

Keep other applications out of the game workspace. Native swaps, split
rotations, resizing and floating are supported; moving a tile to another
workspace ends the session. Hazards use nine screen sectors and classify each
window by its center. Collision uses destination geometry during native window
animations. Projectiles are drawn inside windows rather than being separate
compositor windows. This remains a prototype with further balancing expected.

## Checks

```sh
python -m unittest -v
./play --smoke-test
./play --combat-smoke-test
```

Live checks temporarily open their own board. Run them one at a time and leave
that workspace focused. They exercise physical swaps, shooting, growth, wing
movement/merging, flight/landing, fullscreen, boss transitions, persistent ship
identity and restart cleanup. Rule tests cover lesson sequencing, instruction
pauses, customized hint labels, aiming guidance and random asteroid clusters.

Earlier versions are preserved as Git tags: `v0.1.0` is the initial dodge
prototype; `v0.2.0` adds combat and window abilities.

API references: [Hyprland dispatchers](https://github.com/hyprwm/hyprland-wiki/blob/main/content/configuring/core/dispatchers.md),
[Dwindle layout](https://github.com/hyprwm/hyprland-wiki/blob/main/content/configuring/layouts/dwindle-layout.md),
[window rules](https://github.com/hyprwm/hyprland-wiki/blob/main/content/configuring/core/rules/window-rules.md).

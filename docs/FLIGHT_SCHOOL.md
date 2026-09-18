# Flight School

Run `./play` from the repository root.

## Choose a lesson

```sh
./play
./play --lesson lasers
./play --lesson shoot
./play --lesson float
./play --lesson invasion
```

Press **Space** to start. Finish a lesson, then press Space for the next one.
**R** retries the current lesson; **1–6** jumps to a lesson; **Escape** quits.
**Super+W** also quits, except on enemy/friendly ships during active target
practice. Closing your cyan ship always quits and returns to Omatari when launched there.
Super means the Windows key. Your normal desktop bindings remain active.

## Flight school

| Phase | Game | Task |
| --- | --- | --- |
| 1 | Asteroid field | Super+Shift+arrows moves the ship through all 24 tiles (6 × 4). Dodge 12 impacts. Overlapping bursts arrive every 1.2–2 seconds, with solo rocks and clusters of up to 6. Each rock gets a 2.6-second countdown; at most 10 sectors are threatened at once. |
| 2 | Laser gates | Only 2 windows. Super+J rotates the split; Super+Shift+arrows swaps sides. Move to the marked safe half for 4 gates. |
| 3 | Target practice | Super+arrows selects a red enemy. Super+W closes that actual window and destroys the ship. Close 10 red enemies in a 16-window formation; protect the 5 green friendlies and your cyan ship. |
| 4 | Docking | Super+T undocks a compact ship. Hold Super and left-drag the entire window into the large green bay. When it says ALIGNED, Super+T docks. |
| 5 | Cargo bay | Super+minus/equals changes width. Reach 120%, then restore 100%. |
| 6 | Secret weapon | An invasion approaches. Fullscreen charges the weapon for 2.5 seconds; maximize releases a shockwave that destroys the fleet. |

The game displays the next action needed, progress, and a completion screen.
Friendlies have green borders, shield emblems, and DO NOT FIRE labels.
Closing a friendly retries target practice with a FRIENDLY HIT explanation.
Mistakes give feedback and another attempt. Closing the wrong tile restores the
current exercise with an explanation. Selecting a window alone never destroys it.
There is no auto-fire, health, energy, boss, or combined survival mode.

Fullscreen, maximize, float, split, and close hints are read from your installed
binding descriptions. Follow the on-screen labels for your configuration.

## Requirements and workspace

Flight School requires the dwindle layout with `preserve_split` and
`use_active_for_splits` enabled. Its board uses the first free workspace starting
at 90. Temporary rules are scoped to its own windows and disabled on exit.
Leaving the workspace pauses progress.

`./play --smoke-test` exercises the lessons with real native windows; it is a live
desktop test, not part of the headless suite.

# Quattro: Chase the Sun

A playful sunset stunt scene across three real floating Hyprland windows:
launch ramp, sun and clouds, and a descending landing ramp with a Quattro banner.

```bash
python experiments/quattro-jump/main.py
```

Hold **Space** to charge and release to launch. After landing or missing,
hold Space again for another jump. **R** resets the car without moving windows;
**Esc** closes the scene. Drag the windows to arrange your own route.

There are no scores, challenges or passport updates. The previous passport
file is left untouched. A comet trail follows the car, the banner moves in the
wind, and each flight through the sun window sets off fireworks once per jump.
Use **↑ / ↓** or the **− / +** controls in the launch window to change the ramp
angle from 8° to 38° before launching. The visible ramp and launch velocity use
the same slope. Resetting retains your chosen angle and window positions.

A new workspace is selected automatically. Temporary rules are removed on exit.
Requires Omarchy/Hyprland Lua IPC, GTK3 and Cairo. No desktop config is modified.

The car is drawn inside each of the three windows using desktop coordinates.
It is clipped in uncovered gaps, while physics continues. Position the sun
window along the flight path for continuous visibility. The landing surface,
collision and car pitch follow the same descending ramp.

Tests: `python -m unittest discover -s experiments/quattro-jump -p test_model.py`

Ambient animation includes wind-blown grass and dust, drifting sunset motes,
faster layered clouds, birds and a breathing sun halo. Charging shakes the car
and stirs dust; touchdown adds suspension bounce and a dust puff. The smaller
roadside banner ripples in the wind. Redraws pause on hidden workspaces.

The Quattro is drawn at 78% of its original size. Roadside scrub uses stable,
irregular clusters with varied heights and scattered rocks. Leaving the launch
lip releases an expanding pink/gold dust cloud and grit, anchored to the ramp.

Touchdown wakes up the finish scene: three silhouetted photographers fire a
short staggered sequence of flashes, the brake lights glow during the slide,
and a gust whips the banner before settling back to the ambient breeze.

# Rain + fire: Hyprland window toy

Two real floating GTK windows. Move the cloud above the fire and its rain
extinguishes the flames underneath, using their desktop positions. Partial
alignment cools only the flames in the rain column. Fire slowly recovers when
the rain moves away; fully extinguishing it wins.

```sh
python experiments/rain-fire/main.py
```

Requires the current Omarchy/Hyprland Lua IPC and Python GTK 3 + Cairo (already
available on this machine).

- Drag either window by clicking anywhere inside, or use your usual Hyprland move gesture.
- Keep the cloud above the fire, with their horizontal centers aligned.
- **R** relights the fire. **Esc** or closing either window closes both.

Rules are temporary and scoped to this process's window titles. No installed
configuration files are modified. The DOOM experiment is not involved.

This POC draws rain inside the two windows; rain through the desktop gap would
require an additional transparent overlay. Other windows do not block the rain.

Checked real-window tracking and partial cooling. Geometry checks cover full alignment, no horizontal overlap, a cloud below the fire, and different workspaces. The automated full-extinction check was interrupted by interactive window movement.
Window rules follow the [Hyprland documentation](https://wiki.hypr.land/Configuring/Basics/Window-Rules/).

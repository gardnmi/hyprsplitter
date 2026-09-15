#!/usr/bin/env python3
"""Hyprsplitter: a game played with nine real Hyprland tiles."""

import argparse
import json
import os
import signal
import socket
import sys
import time

from game import Game


class Hyprland:
    def __init__(self):
        signature = os.environ.get("HYPRLAND_INSTANCE_SIGNATURE")
        runtime = os.environ.get("XDG_RUNTIME_DIR")
        if not signature or not runtime:
            raise RuntimeError("Run this inside your Hyprland session.")
        self.path = f"{runtime}/hypr/{signature}/.socket.sock"

    def request(self, command, parse=False):
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as connection:
            connection.settimeout(2)
            connection.connect(self.path)
            connection.sendall((("j/" if parse else "/") + command).encode())
            data = bytearray()
            while chunk := connection.recv(65536):
                data.extend(chunk)
        result = data.decode()
        if parse:
            return json.loads(result)
        if result.strip() != "ok":
            raise RuntimeError(f"Hyprland rejected {command}: {result}")
        return result

    def run(self, *actions):
        self.request("eval " + "; ".join(f"hl.dispatch({action})" for action in actions))

    def focus(self, address):
        self.run(f'hl.dsp.focus({{window="address:{address}"}})')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke-test", action="store_true", help="Build the real board, verify swaps and cleanup, then exit")
    args = parser.parse_args()
    hypr = Hyprland()
    # The prototype targets the Lua dispatcher API used by this installation.
    version = hypr.request("version", True)
    if not version.get("version", "").startswith("0.56"):
        print("Note: tested on Hyprland 0.56.2; requires the Lua dispatcher API.")
    if hypr.request("getoption general:layout", True).get("str") != "dwindle":
        raise RuntimeError("This prototype requires the dwindle layout.")
    if not hypr.request("getoption dwindle:preserve_split", True).get("bool"):
        raise RuntimeError("This prototype requires dwindle:preserve_split enabled.")
    if not hypr.request("getoption dwindle:use_active_for_splits", True).get("bool"):
        raise RuntimeError("This prototype requires dwindle:use_active_for_splits enabled.")

    import gi
    gi.require_version("Gtk", "3.0")
    gi.require_version("Gdk", "3.0")
    gi.require_version("GLibUnix", "2.0")
    from gi.repository import Gdk, GLib, GLibUnix, Gtk
    from render import draw_tile

    class App:
        def __init__(self):
            self.game = Game()
            self.windows = {}
            self.addresses = {}
            self.slots = {}
            self.closing = False
            self.ready = False
            self.away = False
            self.error = None
            self.last_move = 0
            self.previous = hypr.request("activeworkspace", True)["name"]
            self.previous_window = hypr.request("activewindow", True).get("address")
            occupied = {w["id"] for w in hypr.request("workspaces", True)}
            self.workspace = next(i for i in range(90, 10000) if i not in occupied)
            self.prefix = f"Hyprsplitter-{os.getpid()}"
            self.rule = f"hyprsplitter_{os.getpid()}"
            self.steps = iter([(0, None, None, None), (1, 0, "r", .666667),
                               (2, 1, "r", 1), (3, 0, "d", .666667),
                               (6, 3, "d", 1), (4, 1, "d", .666667),
                               (7, 4, "d", 1), (5, 2, "d", .666667), (8, 5, "d", 1)])
            self.pending = None
            self.created_at = time.monotonic()
            self.last_tick = self.created_at
            self.last_sync = 0
            self.smoke_stage = 0
            self.smoke_time = 0
            self.rule_installed = False

        def begin(self):
            hypr.request(f'eval {self.rule} = hl.window_rule({{name="{self.rule}", '
                         f'match={{initial_title="^{self.prefix}-.*$"}}, '
                         f'workspace="{self.workspace}", tile=true, '
                         'opacity="1 override 1 override", no_anim=false})')
            self.rule_installed = True
            hypr.run(f'hl.dsp.focus({{workspace="{self.workspace}"}})')
            GLib.timeout_add(80, self.setup)
            GLib.timeout_add(33, self.tick)

        def guarded(self, fn):
            try:
                return fn()
            except Exception as error:
                self.error = str(error)
                print(f"ERROR: {error}", file=sys.stderr, flush=True)
                self.close()
                return False

        def setup(self):
            return self.guarded(self.setup_step)

        def setup_step(self):
            if self.closing:
                return False
            if time.monotonic() - self.created_at > 20:
                raise RuntimeError("Timed out building the tiled board.")
            if self.pending:
                index, ratio = self.pending
                clients = hypr.request("clients", True)
                found = next((c for c in clients if c["initialTitle"] == f"{self.prefix}-{index}"), None)
                if found is None:
                    return True
                if found["workspace"]["id"] != self.workspace or found["floating"]:
                    raise RuntimeError("A game window did not tile on the game workspace.")
                self.addresses[index] = found["address"]
                hypr.focus(found["address"])
                if ratio:
                    hypr.run(f'hl.dsp.layout("splitratio {ratio} exact")')
                self.pending = None
            step = next(self.steps, None)
            if step is None:
                self.sync()
                self.validate_grid()
                self.ready = True
                hypr.focus(self.addresses[4])
                print(f"READY workspace={self.workspace} ship={self.addresses[4]}", flush=True)
                if args.smoke_test:
                    self.smoke_time = time.monotonic()
                return False
            index, parent, direction, ratio = step
            if parent is not None:
                hypr.focus(self.addresses[parent])
                hypr.run(f'hl.dsp.layout("preselect {direction}")')
            win = Gtk.Window(title=f"{self.prefix}-{index}")
            win.set_decorated(False)
            win.set_default_size(480, 300)
            win.connect("delete-event", lambda *_: self.close() or True)
            win.connect("key-press-event", self.key)
            area = Gtk.DrawingArea()
            area.connect("draw", lambda widget, cr, i=index: draw_tile(
                cr, widget.get_allocated_width(), widget.get_allocated_height(),
                self.game, self.slots.get(i, i), i == 4, self.ready,
                self.away, time.monotonic()))
            win.add(area)
            self.windows[index] = win
            win.show_all()
            self.pending = (index, ratio)
            return True

        def sync(self):
            clients = hypr.request("clients", True)
            by_address = {c["address"]: c for c in clients}
            if any(a not in by_address for a in self.addresses.values()):
                raise RuntimeError("A game tile was closed. Exiting the whole board.")
            self.geometry = {i: by_address[a] for i, a in self.addresses.items()}
            if any(c["workspace"]["id"] != self.workspace or c["floating"] for c in self.geometry.values()):
                raise RuntimeError("A tile left the game board. Restart to rebuild it.")
            ordered = sorted(self.geometry, key=lambda i: self.geometry[i]["at"][1] + self.geometry[i]["size"][1] / 2)
            self.slots = {}
            for row in range(3):
                group = sorted(ordered[row*3:row*3+3], key=lambda i: self.geometry[i]["at"][0])
                for col, index in enumerate(group):
                    self.slots[index] = row*3 + col
            self.game.ship = self.slots[4]
            current = hypr.request("activeworkspace", True)
            self.away = current["id"] != self.workspace
            focused = next((c for c in clients if c.get("focusHistoryID") == 0), None)
            if focused and focused["address"] not in self.addresses.values():
                self.away = True

        def validate_grid(self):
            widths = [c["size"][0] for c in self.geometry.values()]
            heights = [c["size"][1] for c in self.geometry.values()]
            if max(widths) / min(widths) > 1.15 or max(heights) / min(heights) > 1.15:
                raise RuntimeError("Could not form an even 3×3 board with the current layout settings.")

        def move(self, direction):
            if not self.ready or self.game.phase == "over" or self.away:
                return
            if time.monotonic() - self.last_move < .11:
                return
            self.sync()
            target_slot = self.game.neighbor(direction)
            if target_slot is None:
                return
            target = next(i for i, slot in self.slots.items() if slot == target_slot)
            hypr.run(f'hl.dsp.focus({{window="address:{self.addresses[4]}"}})',
                     f'hl.dsp.window.swap({{target="address:{self.addresses[target]}"}})')
            self.sync()
            self.last_move = time.monotonic()

        def key(self, _window, event):
            def handle():
                key = Gdk.keyval_name(event.keyval).lower()
                if key in ("escape", "q"):
                    self.close()
                elif self.ready:
                    directions = {"w": "up", "a": "left", "s": "down", "d": "right",
                                  "up": "up", "left": "left", "down": "down", "right": "right"}
                    if key in directions:
                        self.move(directions[key])
                    elif key in ("space", "return"):
                        if self.game.phase == "ready":
                            self.game.start()
                        elif self.game.phase != "over":
                            self.game.paused = not self.game.paused
                    elif key == "r":
                        self.game.restart()
                        self.sync()
                return True
            return self.guarded(handle)

        def tick(self):
            return self.guarded(self.frame)

        def frame(self):
            if self.closing:
                return False
            now = time.monotonic()
            dt = min(now - self.last_tick, .1)
            self.last_tick = now
            if self.ready:
                if now - self.last_sync > .25:
                    self.sync()
                    self.last_sync = now
                if not self.away:
                    self.game.advance(dt)
                if args.smoke_test:
                    self.smoke(now)
            for window in self.windows.values():
                window.queue_draw()
            return not self.closing

        def smoke(self, now):
            if now - self.smoke_time < .5:
                return
            self.smoke_time = now
            route = [("left", 3), ("up", 0), ("right", 1), ("down", 4), ("right", 5), ("down", 8), ("left", 7), ("up", 4)]
            if self.smoke_stage < len(route):
                direction, expected = route[self.smoke_stage]
                before = self.addresses[4]
                self.move(direction)
                assert self.game.ship == expected, (direction, self.game.ship, expected)
                assert self.addresses[4] == before
                self.validate_grid()
                print(f"PASS real window swap {direction}: slot {expected}", flush=True)
                self.smoke_stage += 1
            else:
                print("PASS nine native tiled windows; eight swaps; grid preserved", flush=True)
                self.close()

        def close(self):
            if self.closing:
                return
            self.closing = True
            for window in self.windows.values():
                window.destroy()
            try:
                if self.rule_installed:
                    hypr.request(f"eval if {self.rule} then {self.rule}:set_enabled(false); {self.rule}=nil end")
                active = hypr.request("activeworkspace", True)
                if active["id"] == self.workspace:
                    hypr.run(f"hl.dsp.focus({{workspace={json.dumps('name:' + self.previous if not self.previous.isdigit() else self.previous)}}})")
                    existing = {c["address"] for c in hypr.request("clients", True)}
                    if self.previous_window in existing:
                        hypr.focus(self.previous_window)
            except Exception as error:
                print(f"Cleanup: {error}", file=sys.stderr)
            if Gtk.main_level():
                Gtk.main_quit()

    GLib.set_prgname("hyprsplitter")
    GLib.set_application_name("Hyprsplitter")
    app = App()
    for sig in (signal.SIGINT, signal.SIGTERM):
        GLibUnix.signal_add(GLib.PRIORITY_DEFAULT, sig, lambda: app.close() or False)
    try:
        app.begin()
        Gtk.main()
    finally:
        app.close()
    return 1 if app.error else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (RuntimeError, OSError, ImportError) as error:
        print(f"Hyprsplitter: {error}", file=sys.stderr)
        sys.exit(1)

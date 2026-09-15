#!/usr/bin/env python3
"""Hyprsplitter: a game played with nine real Hyprland tiles."""

import argparse
import json
import math
import os
import signal
import socket
import sys
import time
import traceback

from game import Game
from combat import center, neighbor, firing_lane, aim_guidance
from controls import LESSONS, shortcut_labels


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
    parser.add_argument("--combat-smoke-test", action="store_true", help="Verify native abilities and all boss window transitions, then exit")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--boss", action="store_true", help="Start with the Window Devourer on launch")
    mode.add_argument("--arcade", action="store_true", help="Skip lessons and use the original fast difficulty")
    mode.add_argument("--lesson", choices=[lesson[1] for lesson in LESSONS], help="Jump to a particular training lesson")
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
            self.game = Game(training=not (args.boss or args.arcade or args.smoke_test or args.combat_smoke_test))
            self.game.controls = shortcut_labels(hypr.request("binds", True))
            self.reset_game()
            self.windows = {}
            self.addresses = {}
            self.slots = {}
            self.positions = {i: i for i in range(9)}
            self.controlled = 4
            self.fire_key = None
            self.applied = (False, 0, False, False)
            self.rebuilding = False
            self.native_fullscreen = False
            self.last_boss_move = 0
            self.last_native_float = False
            self.last_native_mode = 0
            self.external_layout = False
            self.native_maximized = False
            self.focused_actor = 4
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

        def reset_game(self):
            self.game.restart()
            if args.boss:
                self.game.wave = 4
            elif args.lesson:
                lesson = next(item for item in LESSONS if item[1] == args.lesson)
                self.game.wave = lesson[0]
                self.game.lesson = lesson[1]
                self.game.phase = "briefing"
                self.game.enemies = {}

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
                self.error = f"{type(error).__name__}: {error}"
                traceback.print_exc()
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
                if args.smoke_test or args.combat_smoke_test:
                    self.smoke_time = time.monotonic()
                return False
            index, parent, direction, ratio = step
            if parent is not None:
                hypr.focus(self.addresses[parent])
                hypr.run(f'hl.dsp.layout("preselect {direction}")')
            self.new_window(index)
            self.pending = (index, ratio)
            return True

        def new_window(self, index):
            win = Gtk.Window(title=f"{self.prefix}-{index}")
            win.set_decorated(False)
            win.set_default_size(480, 300)
            win.connect("delete-event", lambda *_: self.close() or True)
            win.connect("key-press-event", self.key)
            win.connect("key-release-event", self.key_release)
            win.connect("focus-out-event", lambda *_: self.release_fire())
            area = Gtk.DrawingArea()
            area.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
            area.connect("button-press-event", self.click, index)
            area.connect("draw", lambda widget, cr, i=index: draw_tile(
                cr, widget.get_allocated_width(), widget.get_allocated_height(),
                self.game, self.slots.get(i, i), i == 4, self.ready,
                self.away, time.monotonic(), actor=i, controlled=self.focused_actor))
            win.add(area)
            self.windows[index] = win
            win.show_all()

        def release_fire(self):
            self.fire_key = None
            return False

        def key_release(self, _window, event):
            if Gdk.keyval_name(event.keyval).lower() in ("i", "j", "k", "l"):
                self.release_fire()
            return True

        def sync(self, observe=False):
            clients = hypr.request("clients", True)
            by_address = {c["address"]: c for c in clients}
            if any(a not in by_address for a in self.addresses.values()):
                raise RuntimeError("A game tile was closed. Exiting the whole board.")
            previous = getattr(self, "geometry", {})
            self.geometry = {i: by_address[a] for i, a in self.addresses.items()}
            if any(c["workspace"]["id"] != self.workspace for c in self.geometry.values()):
                raise RuntimeError("A tile left the game board. Restart to rebuild it.")
            if observe:
                self.observe_desktop(previous)
            if not hasattr(self, "arena"):
                x = min(c["at"][0] for c in self.geometry.values())
                y = min(c["at"][1] for c in self.geometry.values())
                right = max(c["at"][0] + c["size"][0] for c in self.geometry.values())
                bottom = max(c["at"][1] + c["size"][1] for c in self.geometry.values())
                self.arena = x, y, right - x, bottom - y
            # Physical centers determine hazard sectors even after resizing/splitting.
            # Hyprland reports destination geometry while its native animation runs.
            if not self.native_fullscreen and not self.native_maximized:
                x, y, w, h = self.arena
                self.slots = {i: min(2, max(0, int((center(c)[1]-y)/h*3)))*3 +
                              min(2, max(0, int((center(c)[0]-x)/w*3))) for i, c in self.geometry.items()}
                self.game.ship = self.slots[4]
                self.game.wing = self.slots.get(9)
            current = hypr.request("activeworkspace", True)
            self.away = current["id"] != self.workspace
            focused = next((c for c in clients if c.get("focusHistoryID") == 0), None)
            self.focused_actor = next((i for i, a in self.addresses.items() if focused and a == focused["address"]), None)
            if self.focused_actor in (4, 9):
                self.controlled = self.focused_actor
            if focused and focused["address"] not in self.addresses.values():
                self.away = True
            if self.away:
                self.release_fire()
            self.last_native_float = self.geometry[4]["floating"]
            self.last_native_mode = self.geometry[4].get("fullscreen", 0)
            self.game.is_floating = self.last_native_float

        def observe_desktop(self, previous):
            """Observe real desktop shortcuts. Do not replace or intercept any binding."""
            ship = self.geometry[4]
            floating = ship["floating"]
            mode = ship.get("fullscreen", 0)
            if floating != self.last_native_float:
                self.game.flight = 3 if floating else 0
                self.external_layout = True
                self.game.message = "FLOATING / USE SUPER + LEFT-DRAG" if floating else "LANDED / TILING RESTORED"
            if mode != self.last_native_mode:
                self.external_layout = True
                if mode == 2:
                    if not self.game.ability("fullscreen"):
                        self.game.burst = .9  # Practice still demonstrates real fullscreen.
                    self.native_fullscreen = True
                    self.native_maximized = False
                elif mode == 1:
                    self.native_maximized = True
                    self.native_fullscreen = False
                    self.game.burst = 0
                    self.game.growth = 5
                else:
                    self.native_maximized = False
                    self.native_fullscreen = False
                    self.game.burst = 0
            old_ship = previous.get(4)
            if old_ship and not mode and not floating and not self.last_native_mode:
                if math.prod(ship["size"]) > math.prod(old_ship["size"])*1.08:
                    self.game.growth = 5
                    self.external_layout = True
                    self.game.message = "RESIZED / DOUBLE DAMAGE FOR 5 SECONDS"
            # Exact exchanged rectangles identify native swaps without treating a
            # split rotation or resize as a swap. Keep structural leaves in sync.
            used = set()
            for i, before in previous.items():
                if i in used or i not in self.geometry:
                    continue
                for j, other in previous.items():
                    if j <= i or j in used or j not in self.geometry:
                        continue
                    if (self.geometry[i]["at"] == other["at"] and
                            self.geometry[j]["at"] == before["at"] and before["at"] != other["at"]):
                        self.positions[i], self.positions[j] = self.positions[j], self.positions[i]
                        used.update((i, j))
                        self.game.message = "WINDOW SWAPPED"
                        break

        def click(self, widget, event, index):
            if not self.ready or self.rebuilding or index != 4:
                return False
            scale = min(widget.get_allocated_width()/440, widget.get_allocated_height()/290, 1.35)
            width = widget.get_allocated_width()/scale
            if 47 <= event.y/scale <= 75 and width-158 <= event.x/scale <= width-16:
                if not self.game.training or self.game.wave >= 16:
                    self.game.ability("split")
            return True

        def selector(self, index):
            return f'"address:{self.addresses[index]}"'

        def native_signature(self):
            return self.game.split, self.game.boss, bool(self.game.growth), bool(self.game.flight)

        def rebuild(self):
            """Rebuild only our own tiling tree, preserving surviving window identities."""
            self.rebuilding = True
            self.rebuild_started = time.monotonic()
            desired = set(range(9))
            if self.game.split:
                desired.add(9)
            if self.game.boss == 2:
                desired.update((10, 11))
            if self.game.flight:
                desired.add(12)  # Landing sector keeps the tiled board occupied.
            if self.game.boss == 3:
                desired.add(13)
            for index in set(self.windows) - desired:
                # Merging a wing restores the background tile displaced from its leaf.
                if index == 9:
                    other = next((i for i, p in self.positions.items() if p == 9 and i != 9), None)
                    if other is not None:
                        self.positions[other] = self.positions[9]
                self.windows.pop(index).destroy()
                self.addresses.pop(index, None)
                self.positions.pop(index, None)
            for index in desired - set(self.windows):
                self.positions[index] = index
                self.new_window(index)
            if 12 in desired:
                self.positions[12] = self.positions[4]
            if 13 in desired:
                self.positions[13] = self.positions[0]
            if self.controlled not in desired:
                self.controlled = 4

        def rebuild_tick(self):
            if time.monotonic() - self.rebuild_started > 8:
                raise RuntimeError("Timed out changing the window formation.")
            clients = {c["initialTitle"]: c for c in hypr.request("clients", True)}
            if any(f"{self.prefix}-{i}" not in clients for i in self.windows):
                return
            self.addresses = {i: clients[f"{self.prefix}-{i}"]["address"] for i in self.windows}
            actions = [f'hl.dsp.window.float({{window={self.selector(i)}, action="on"}})' for i in self.windows]
            floating = set()
            if self.game.flight:
                floating.add(4)
            if self.game.boss == 3:
                floating.add(0)
            occupants = {pos: i for i, pos in self.positions.items() if i not in floating}
            steps = [(0, None, None, None), (1, 0, "r", .666667),
                     (2, 1, "r", 1), (3, 0, "d", .666667), (6, 3, "d", 1),
                     (4, 1, "d", .666667), (7, 4, "d", 1), (5, 2, "d", .666667), (8, 5, "d", 1)]
            if self.game.split:
                steps.append((9, 4, "r", 1))
            if self.game.boss == 2:
                # Split the boss's actual window leaf into three independently drawn windows.
                boss_pos = self.positions[0]
                steps += [(10, boss_pos, "d", .666667), (11, 10, "d", 1)]
            for pos, parent, direction, ratio in steps:
                index = occupants[pos]
                if parent is not None:
                    actions += [f'hl.dsp.focus({{window={self.selector(occupants[parent])}}})',
                                f'hl.dsp.layout("preselect {direction}")']
                actions += [f'hl.dsp.window.float({{window={self.selector(index)}, action="off"}})',
                            f'hl.dsp.focus({{window={self.selector(index)}}})']
                if ratio:
                    actions.append(f'hl.dsp.layout("splitratio {ratio} exact")')
            hypr.run(*actions)
            self.applied = self.native_signature()
            if self.game.boss == 1:
                hypr.run(f'hl.dsp.window.resize({{window={self.selector(0)}, x=180, y=160, relative=true}})')
            if self.game.growth:
                hypr.run(f'hl.dsp.window.resize({{window={self.selector(4)}, x=140, y=100, relative=true}})')
            x, y, w, h = self.arena
            for index in floating:
                old = self.geometry.get(index)
                px, py = center(old) if old else (x+w/2, y+h/2)
                width, height = (240, 190) if index == 4 else (330, 210)
                px = max(x, min(x+w-width, px-width/2))
                py = max(y, min(y+h-height, py-height/2))
                hypr.run(f'hl.dsp.window.resize({{window={self.selector(index)}, x={width}, y={height}}})',
                         f'hl.dsp.window.move({{window={self.selector(index)}, x={int(px)}, y={int(py)}}})')
            self.rebuilding = False
            self.sync()
            hypr.focus(self.addresses[self.controlled])

        def fire(self, direction):
            if self.rebuilding or self.away or self.native_fullscreen:
                return
            targets, tiles = [], []
            for source in ([4, 9] if self.game.split else [4]):
                target, path = firing_lane(self.geometry, source, self.game.enemies, direction)
                if target is not None:
                    targets.append(target)
                tiles.extend(path)
            self.game.fire(direction, targets, tiles)

        def auto_fire(self):
            if self.rebuilding:
                return
            self.game.locked_target, self.game.aim_hint = aim_guidance(self.geometry, 4, self.game.enemies)
            sources = [4, 9] if self.game.split else [4]
            if any(firing_lane(self.geometry, source, self.game.enemies, "up")[0] is not None for source in sources):
                self.fire("up")

        def validate_grid(self):
            widths = [c["size"][0] for c in self.geometry.values()]
            heights = [c["size"][1] for c in self.geometry.values()]
            if max(widths) / min(widths) > 1.15 or max(heights) / min(heights) > 1.15:
                raise RuntimeError("Could not form an even 3×3 board with the current layout settings.")

        def move(self, direction):
            if not self.ready or self.rebuilding or self.game.phase in ("over", "victory") or self.away or self.native_fullscreen:
                return
            if time.monotonic() - self.last_move < .11:
                return
            self.sync()
            source = self.controlled
            if source == 4 and self.game.flight:
                dx, dy = {"left": (-85, 0), "right": (85, 0), "up": (0, -65), "down": (0, 65)}[direction]
                c = self.geometry[4]
                x, y, w, h = self.arena
                px = max(x, min(x+w-c["size"][0], c["at"][0]+dx))
                py = max(y, min(y+h-c["size"][1], c["at"][1]+dy))
                hypr.run(f'hl.dsp.window.move({{window={self.selector(4)}, x={int(px)}, y={int(py)}}})')
                self.last_move = time.monotonic()
                self.sync()
                return
            blocked = set(self.game.enemies) if self.game.playing else set()
            blocked.update((4, 9, 12, 13))
            target = neighbor(self.geometry, source, direction, blocked)
            if target is None:
                return
            hypr.run(f'hl.dsp.focus({{window={self.selector(source)}}})',
                     f'hl.dsp.window.swap({{target="address:{self.addresses[target]}"}})')
            self.positions[source], self.positions[target] = self.positions[target], self.positions[source]
            self.sync()
            self.last_move = time.monotonic()

        def key(self, _window, event):
            def handle():
                key = Gdk.keyval_name(event.keyval).lower()
                if event.state & (Gdk.ModifierType.SUPER_MASK | Gdk.ModifierType.MOD4_MASK | Gdk.ModifierType.MOD1_MASK | Gdk.ModifierType.CONTROL_MASK):
                    return False
                if key in ("escape", "q"):
                    self.close()
                elif self.ready and not self.rebuilding:
                    if key in ("space", "return"):
                        if self.game.phase in ("ready", "briefing"):
                            self.game.start()
                        elif self.game.phase not in ("over", "victory"):
                            self.game.paused = not self.game.paused
                    elif key == "r":
                        self.reset_game()
                        self.controlled = 4
                        self.release_fire()
                        self.external_layout = False
                        self.native_maximized = False
                        hypr.run(f'hl.dsp.window.fullscreen({{window={self.selector(4)}, mode="fullscreen", action="unset"}})')
                        self.rebuild()
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
                if self.rebuilding:
                    self.rebuild_tick()
                    return True
                if now - self.last_sync > .08:
                    self.sync(observe=not (args.smoke_test or args.combat_smoke_test))
                    self.last_sync = now
                want_fullscreen = bool(self.game.burst)
                if want_fullscreen != self.native_fullscreen:
                    hypr.run(f'hl.dsp.window.fullscreen({{window={self.selector(4)}, mode="fullscreen", action="{"set" if want_fullscreen else "unset"}"}})')
                    self.native_fullscreen = want_fullscreen
                    self.last_native_mode = 2 if want_fullscreen else 0
                structural_change = self.native_signature()[:2] != self.applied[:2] or (12 in self.windows and not self.game.flight)
                if self.external_layout and not structural_change:
                    self.applied = self.native_signature()
                if (structural_change or self.native_signature() != self.applied) and not self.native_fullscreen and not self.native_maximized:
                    self.rebuild()
                    return True
                if not self.away and not args.combat_smoke_test:
                    self.game.advance(dt)
                    self.auto_fire()
                    if self.game.boss == 3 and self.game.playing and not self.native_fullscreen and now - self.last_boss_move > .1:
                        x, y, w, h = self.arena
                        bx = x + (w-330) * (.5 + .45*math.sin(now*.8))
                        by = y + h*.08
                        hypr.run(f'hl.dsp.window.move({{window={self.selector(0)}, x={int(bx)}, y={int(by)}}})')
                        self.last_boss_move = now
                if args.smoke_test:
                    self.smoke(now)
                elif args.combat_smoke_test:
                    self.combat_smoke(now)
            for window in self.windows.values():
                window.queue_draw()
            return not self.closing

        def combat_smoke(self, now):
            if now - self.smoke_time < .7:
                return
            self.smoke_time = now
            self.sync()
            stage = self.smoke_stage
            if stage == 0:
                self.original_ship = self.addresses[4]
                self.normal_area = math.prod(self.geometry[4]["size"])
                self.game.start()
                self.move("left")
                self.fire("up")
                assert self.game.enemies[0] == 2
                print("PASS controller shooting hits aligned enemy", flush=True)
                self.last_move = 0
                self.move("right")
                assert self.game.ability("grow")
            elif stage == 1:
                assert math.prod(self.geometry[4]["size"]) > self.normal_area, self.geometry[4]["size"]
                print("PASS native ship growth", flush=True)
                self.game.growth = 0
                self.game.energy = 100
                assert self.game.ability("split")
            elif stage == 2:
                assert 9 in self.geometry and not self.geometry[9]["floating"]
                assert self.addresses[4] == self.original_ship
                self.controlled = 9
                before = self.positions[9]
                self.last_move = 0
                self.move("down")
                assert self.positions[9] != before
                print("PASS second ship window split from formation", flush=True)
                self.game.ability("split")
                self.game.energy = 100
                assert self.game.ability("float")
            elif stage == 3:
                assert self.geometry[4]["floating"] and 12 in self.geometry
                before = self.geometry[4]["at"][:]
                self.move("right")
                assert self.geometry[4]["at"] != before
                print("PASS free floating flight with landing sector", flush=True)
                self.game.flight = 0
            elif stage == 4:
                assert not self.geometry[4]["floating"] and 12 not in self.geometry
                print("PASS ship landed back in tiling tree", flush=True)
                self.game.energy = 100
                self.game.ability("fullscreen")
            elif stage == 5:
                assert self.geometry[4].get("fullscreen", 0) != 0
                print("PASS native fullscreen nova", flush=True)
                self.game.burst = 0
                self.game.boss = 1
                self.game.enemies = {0: 18}
            elif stage == 6:
                assert self.geometry[4].get("fullscreen", 0) == 0
                assert math.prod(self.geometry[0]["size"]) > self.normal_area
                print("PASS giant boss window", flush=True)
                self.game.damage(0, 18)
            elif stage == 7:
                assert {10, 11}.issubset(self.geometry)
                print("PASS boss fractured into three real windows", flush=True)
                for index in (0, 10, 11):
                    self.game.damage(index, 6)
            elif stage == 8:
                assert self.geometry[0]["floating"]
                assert 10 not in self.geometry and 11 not in self.geometry
                print("PASS detached floating boss core", flush=True)
                self.game.damage(0, 12)
            elif stage == 9:
                assert self.game.phase == "victory"
                assert not self.geometry[0]["floating"]
                assert self.addresses[4] == self.original_ship
                print("PASS victory and persistent ship window identity", flush=True)
                self.game.restart()
            else:
                self.validate_grid()
                assert len(self.geometry) == 9
                print("PASS restart restored nine-tile board", flush=True)
                self.close()
            self.smoke_stage += 1

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

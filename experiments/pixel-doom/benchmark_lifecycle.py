#!/usr/bin/env python3
"""Bounded lifecycle A/B test inside the private, nested-only Hyprland build.

Never targets the desktop's IPC socket. Requires hyprland-batch-lifecycle.patch.
Creates at most 1024 static held Foot windows; does not measure DOOM playback FPS.
"""
import argparse
import json
import os
from pathlib import Path
import re
import signal
import socket
import subprocess
import tempfile
import time

from foot_ipc import open_window

ROOT = Path(__file__).resolve().parent


def request(path, command):
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
        sock.settimeout(15)
        sock.connect(str(path))
        sock.sendall(command.encode())
        chunks = []
        while chunk := sock.recv(65536):
            chunks.append(chunk)
    return b''.join(chunks).decode()


def wait_for(check, seconds=20):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        result = check()
        if result:
            return result
        time.sleep(.02)
    raise TimeoutError('Nested benchmark condition timed out')


def cpu_seconds(pid):
    fields = Path(f'/proc/{pid}/stat').read_text().rsplit(')', 1)[1].split()
    return (int(fields[11]) + int(fields[12])) / os.sysconf('SC_CLK_TCK')


def stop(proc):
    if proc is not None and proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)


def trial(binary, foot, count, enabled, repeat, out, mode="lifecycle"):
    label = f'{mode}-{count}-{"batch" if enabled else "baseline"}-{repeat}'
    result = dict(count=count, mode=mode, optimized=enabled, batching=(enabled or mode != 'lifecycle'), repeat=repeat, status='failed')
    compositor = None
    servers = []
    with tempfile.TemporaryDirectory(prefix='pdn-') as directory:
        tmp = Path(directory)
        runtime = tmp / 'r'
        runtime.mkdir(mode=0o700)
        config = tmp / 'hyprland.lua'
        config.write_text('''hl.monitor({output="", mode="800x600@60", position="auto", scale=1})
hl.config({
  animations={enabled=false},
  general={border_size=0, gaps_in=0, gaps_out=0},
  decoration={rounding=0, blur={enabled=false}, shadow={enabled=false}},
  misc={disable_hyprland_logo=true, disable_splash_rendering=true, disable_watchdog_warning=true},
  debug={disable_logs=false}
})
hl.window_rule({name="lifecycle", match={class="^pixel-doom-.*$"}, float=true,
  size={24,24}, no_anim=true, no_initial_focus=true, no_shadow=true, no_blur=true})
''')
        env = os.environ.copy()
        parent_display = Path(env['WAYLAND_DISPLAY'])
        if not parent_display.is_absolute():
            parent_display = Path(env['XDG_RUNTIME_DIR']) / parent_display
        env.update(XDG_RUNTIME_DIR=str(runtime), WAYLAND_DISPLAY=str(parent_display),
                   HYPRLAND_NO_SD_VARS='1', HYPRLAND_PIXEL_DOOM_NESTED_ONLY='1',
                   HYPRLAND_PIXEL_DOOM_BATCH_MS='8')
        for key in ('HYPRLAND_INSTANCE_SIGNATURE', 'HYPRLAND_CMD', 'HYPRLAND_PIXEL_DOOM_BATCH_LIFECYCLE',
                    'FOOT_PIXEL_DOOM_CACHE', 'FOOT_PIXEL_DOOM_NO_CALLBACK', 'HYPRLAND_PIXEL_DOOM_FAST_ADDRESS',
                    'HYPRLAND_PIXEL_DOOM_SKIP_UNCHANGED_RULES'):
            env.pop(key, None)
        if enabled or mode != 'lifecycle':
            env['HYPRLAND_PIXEL_DOOM_BATCH_LIFECYCLE'] = '1'
        if mode == 'address' and enabled:
            env['HYPRLAND_PIXEL_DOOM_FAST_ADDRESS'] = '1'
        if mode == 'rules' and enabled:
            env['HYPRLAND_PIXEL_DOOM_SKIP_UNCHANGED_RULES'] = '1'
        with (out / f'{label}.log').open('w') as log:
            try:
                compositor = subprocess.Popen(['dbus-run-session', '--', 'sh', '-c',
                    'echo $$ > "$1"; exec "$2" --config "$3"', 'nested',
                    str(tmp / 'pid'), str(binary), str(config)], env=env,
                    stdout=log, stderr=log, start_new_session=True)
                def find_ipc():
                    if compositor.poll() is not None:
                        raise RuntimeError('Nested compositor exited; see log')
                    return next(runtime.glob('hypr/*/.socket.sock'), None)
                ipc = wait_for(find_ipc)
                pid = int((tmp / 'pid').read_text())
                child_display = wait_for(lambda: next((p for p in runtime.glob('wayland-*') if p.is_socket()), None))
                errors = request(ipc, 'configerrors').strip()
                if errors and errors != 'ok':
                    raise RuntimeError(f'Nested config errors: {errors}')
                child_env = env | {'WAYLAND_DISPLAY': str(child_display), 'FOOT_PIXEL_DOOM': '1'}
                def server(name):
                    path = tmp / f'{name}.sock'
                    proc = subprocess.Popen([str(foot), '--config=/dev/null', f'--server={path}',
                        '-o', 'workers=0', '-o', 'scrollback.lines=0', '-o', 'pad=0x0',
                        '-o', 'font=monospace:size=2', '-o', 'resize-by-cells=no',
                        *(['-o', 'tweak.font-monospace-warn=no'] if mode == 'font' and enabled else [])],
                        env=child_env, stdout=log, stderr=log)
                    servers.append(proc)
                    wait_for(lambda: path.exists())
                    return proc, path
                _, anchor = server('anchor')
                open_window(anchor, 'lifecycle-anchor', 'Ordinary anchor', 200, 150, ['/bin/true'], True)
                targets, target_socket = server('targets')
                clients = lambda: json.loads(request(ipc, 'j/clients'))
                wait_for(lambda: len(clients()) == 1)
                start_cpu = cpu_seconds(pid)
                start_foot_cpu = cpu_seconds(targets.pid)
                sample_compositor_cpu = start_cpu
                sample_foot_cpu = start_foot_cpu
                start = time.monotonic()
                result['creation_samples'] = []
                sample_start = start
                for i in range(count):
                    if i % 128 == 0:
                        available = int(next(line.split()[1] for line in Path('/proc/meminfo').read_text().splitlines() if line.startswith('MemAvailable:')))
                        if available < 8 * 1024 * 1024:
                            raise RuntimeError('Stopped at 8 GiB available-memory reserve')
                    if time.monotonic() - start > 45:
                        raise TimeoutError("Window creation exceeded 45 seconds")
                    open_window(target_socket, 'pixel-doom-lifecycle', f'cell-{i}', 24, 24, ['/bin/true'], True)
                    if (i + 1) % 128 == 0:
                        now = time.monotonic()
                        comp_cpu, foot_cpu = cpu_seconds(pid), cpu_seconds(targets.pid)
                        result['creation_samples'].append({'opened': i + 1, 'batch_seconds': now - sample_start,
                            'compositor_cpu_seconds': comp_cpu - sample_compositor_cpu,
                            'foot_cpu_seconds': foot_cpu - sample_foot_cpu})
                        sample_start = now
                        sample_compositor_cpu, sample_foot_cpu = comp_cpu, foot_cpu
                windows = wait_for(lambda: (ws if len(ws := clients()) == count+1 else None), 40)
                result['map_seconds'] = time.monotonic() - start
                result['map_cpu_seconds'] = cpu_seconds(pid) - start_cpu
                result['map_foot_cpu_seconds'] = cpu_seconds(targets.pid) - start_foot_cpu
                result['floating_targets'] = sum(w['floating'] for w in windows if w['class'] == 'pixel-doom-lifecycle')
                if result['floating_targets'] != count:
                    raise RuntimeError('Some target windows were not floating')
                result['size_mismatches'] = sum(w['size'] != [24, 24] for w in windows if w['class'] == 'pixel-doom-lifecycle')
                if result['size_mismatches']:
                    raise RuntimeError('Target window dimensions mismatched')
                time.sleep(.5)
                if mode == 'address':
                    def evaluate(code):
                        answer = request(ipc, 'eval ' + code).strip()
                        if answer != 'ok':
                            raise RuntimeError('Lua probe failed: ' + answer)
                    targets_list = [w for w in windows if w['class'] == 'pixel-doom-lifecycle']
                    addresses = [w['address'] for w in targets_list]
                    address = addresses[0]
                    invalid = ['0x0', '0x', '0xg', '0X' + address[2:], '0x0' + address[2:],
                               address + 'z', '-0x1', '0x' + 'f' * 40]
                    upper = '0x' + address[2:].upper()
                    if upper != address:
                        invalid.append(upper)
                    for candidate in invalid:
                        evaluate(f'assert(hl.get_window({json.dumps("address:" + candidate)}) == nil)')
                    evaluate(f'assert(hl.get_window({json.dumps(" address:" + address + " ")}) ~= nil)')
                    evaluate('assert(hl.get_window("title:^cell-0$") ~= nil)')
                    start_cpu = cpu_seconds(pid)
                    probe_start = time.monotonic()
                    # Read-only selection probe, fixed number of successful queries.
                    for _ in range(16):
                        for offset in range(0, len(addresses), 64):
                            selectors = ','.join(json.dumps('address:' + a) for a in addresses[offset:offset+64])
                            evaluate('for _,s in ipairs({' + selectors + '}) do assert(hl.get_window(s) ~= nil) end')
                    result['lookup_seconds'] = time.monotonic() - probe_start
                    result['lookup_cpu_seconds'] = cpu_seconds(pid) - start_cpu
                    result['lookup_count'] = 16 * count
                    start_cpu = cpu_seconds(pid)
                    probe_start = time.monotonic()
                    for offset in range(0, len(targets_list), 4):
                        commands = []
                        for w in targets_list[offset:offset+4]:
                            index = int(w['title'].split('-')[-1])
                            selector = json.dumps('address:' + w['address'])
                            commands.append(f'hl.dispatch(hl.dsp.window.move({{window={selector},x={index%32*16},y={index//32*16}}}))')
                        evaluate(';'.join(commands))
                    result['placement_seconds'] = time.monotonic() - probe_start
                    result['placement_cpu_seconds'] = cpu_seconds(pid) - start_cpu
                    positioned = [w for w in clients() if w['class'] == 'pixel-doom-lifecycle']
                    result['placement_mismatches'] = sum(w['at'] != [int(w['title'].split('-')[-1])%32*16, int(w['title'].split('-')[-1])//32*16] for w in positioned)
                    if result['placement_mismatches']:
                        raise RuntimeError('Placement geometry mismatched')
                    result['selector_checks'] = 'passed'
                    time.sleep(.5)
                start_cpu = cpu_seconds(pid)
                start = time.monotonic()
                targets.terminate()
                wait_for(lambda: len(clients()) == 1 and targets.poll() is not None, 40)
                # Same settling interval for both modes, including the fixed 8ms timer.
                time.sleep(.025)
                request(ipc, 'j/clients')
                result['unmap_seconds'] = time.monotonic() - start
                result['unmap_cpu_seconds'] = cpu_seconds(pid) - start_cpu
                result['remaining_classes'] = [w['class'] for w in clients()]
                if mode == 'address':
                    evaluate(f'assert(hl.get_window({json.dumps("address:" + address)}) == nil)')
                stop(servers[0])
                wait_for(lambda: len(clients()) == 0)
                result['status'] = 'complete'
            except Exception as error:
                result['error'] = str(error)
            finally:
                for proc in reversed(servers):
                    stop(proc)
                if compositor is not None and compositor.poll() is None:
                    os.killpg(compositor.pid, signal.SIGTERM)
                    try:
                        compositor.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        os.killpg(compositor.pid, signal.SIGKILL)
                        compositor.wait(timeout=5)
                for source in runtime.glob('hypr/*/hyprland.log'):
                    (out / f'{label}-hyprland.log').write_bytes(source.read_bytes())
    counter_log = out / f'{label}-hyprland.log'
    if not counter_log.exists():
        counter_log = out / f'{label}.log'
    text = counter_log.read_text(errors='replace')
    counters = re.findall(r'pixel-doom lifecycle: (\d+) requests, (\d+) workspace passes, decorations=(true|false|0|1)', text)
    result['batch_log_entries'] = len(counters)
    result['batched_requests'] = sum(int(a) for a, _, _ in counters)
    result['workspace_passes'] = sum(int(b) for _, b, _ in counters)
    (out / f'{label}.json').write_text(json.dumps(result, indent=2)+'\n')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--hyprland', type=Path, default=Path('/tmp/pixel-doom-hyprland-build/Hyprland'))
    parser.add_argument('--foot', type=Path, default=Path('/tmp/pixel-doom-foot-build/foot'))
    parser.add_argument('--mode', choices=['lifecycle', 'address', 'font', 'rules'], default='lifecycle')
    parser.add_argument('--count', type=int, default=128)
    parser.add_argument('--repeats', type=int, default=2)
    args = parser.parse_args()
    if not 1 <= args.count <= 1024 or not 1 <= args.repeats <= 3:
        parser.error('Allowed: 1–1024 windows, 1–3 repeats')
    # The special backend guard must exist; accidentally running stock Hyprland is unsafe.
    binary_bytes = args.hyprland.read_bytes()
    if args.mode == 'address' and b'HYPRLAND_PIXEL_DOOM_FAST_ADDRESS' not in binary_bytes:
        parser.error('Binary lacks the address optimization patch')
    if args.mode == 'rules' and b'HYPRLAND_PIXEL_DOOM_SKIP_UNCHANGED_RULES' not in binary_bytes:
        parser.error('Binary lacks the workspace rule optimization patch')
    if b'HYPRLAND_PIXEL_DOOM_NESTED_ONLY' not in binary_bytes:
        parser.error('Binary lacks the mandatory nested-only backend guard')
    out = ROOT / 'output'
    out.mkdir(exist_ok=True)
    results = []
    for repeat in range(args.repeats):
        for enabled in ([False, True] if repeat % 2 == 0 else [True, False]):
            result = trial(args.hyprland.resolve(), args.foot.resolve(), args.count, enabled, repeat, out, args.mode)
            results.append(result)
            print(json.dumps(result), flush=True)
            (out / f'{args.mode}-comparison-{args.count}.json').write_text(json.dumps(results, indent=2)+'\n')
            if result['status'] != 'complete':
                raise SystemExit(1)


if __name__ == '__main__':
    main()

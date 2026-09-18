#!/usr/bin/env python3
"""Run the progressive DOOM sequence inside the private nested compositor."""
import argparse
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
from benchmark_lifecycle import request,wait_for,stop,cpu_seconds

ROOT=Path(__file__).resolve().parent
BINARY=Path('/tmp/pixel-doom-hyprland-build/Hyprland')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--levels',type=int,default=3)
    p.add_argument('--max-terminals',type=int)
    p.add_argument('--timeout',type=float,default=180)
    p.add_argument('--allow-slow',action='store_true')
    p.add_argument('--defer-texture',action='store_true',help='Defer solid-color GPU uploads until ordinary rendering needs them')
    p.add_argument('--skip-unchanged-rules',action='store_true',help='Skip irrelevant workspace rule refreshes for pixel tiles')
    p.add_argument('--fixed-host-size',action='store_true',help='Use an 800x600 floating host for matched small benchmarks')
    p.add_argument('--host-size',choices=['1280x800'],help='Fixed recording host large enough for 64,000 tiles')
    p.add_argument('--combined-geometry',action='store_true',help='Private combined move/resize dispatcher')
    p.add_argument('--fast-floating',action='store_true',help='Private floating-window lookup/layout shortcut')
    p.add_argument('--split-batch',type=int,default=8)
    p.add_argument('--hold',type=float,default=3)
    p.add_argument('--output',type=Path,default=ROOT/'output'/'progressive-preview')
    p.add_argument('--record',action='store_true')
    p.add_argument('--static-grid',action='store_true')
    p.add_argument('--record-parent',action='store_true',help='Capture host window using outer compositor')
    p.add_argument('--host-workspace',type=int,help='Desktop workspace for the disposable host')
    p.add_argument('--focus-for-capture',action='store_true')
    p.add_argument('--prestart-record',action='store_true')
    p.add_argument('--fps',type=int,default=35)
    a=p.parse_args();a.output=a.output.resolve();a.output.mkdir(parents=True,exist_ok=True)
    if (a.output/'close-nested').exists():p.error('Choose a fresh output directory for each run')
    if b'HYPRLAND_PIXEL_DOOM_NESTED_ONLY' not in BINARY.read_bytes():p.error('Private nested-only build required')
    if a.fixed_host_size and a.host_size:p.error('Choose one host size option')
    fixed_size=[1280,800] if a.host_size else ([800,600] if a.fixed_host_size else None)
    if a.combined_geometry and b'HYPRLAND_PIXEL_DOOM_COMBINED_GEOMETRY' not in BINARY.read_bytes():
        p.error('Private combined-geometry build required')
    if a.fast_floating and b'HYPRLAND_PIXEL_DOOM_FAST_FLOATING' not in BINARY.read_bytes():
        p.error('Private fast-floating build required')
    compositor=launcher=None
    with tempfile.TemporaryDirectory(prefix='pg-') as directory, (a.output/'nested.log').open('w') as log:
        root=Path(directory);runtime=root/'r';runtime.mkdir(mode=0o700)
        config=root/'hyprland.lua'
        config.write_text('''hl.monitor({output="",mode="1280x800@60",position="auto",scale=1})
hl.config({animations={enabled=false},general={border_size=0,gaps_in=0,gaps_out=0},
 decoration={rounding=0,blur={enabled=false},shadow={enabled=false}},
 misc={disable_hyprland_logo=true,disable_splash_rendering=true,disable_watchdog_warning=true},debug={disable_logs=false}})
'''.replace('1280x800@60','800x600@60' if a.fixed_host_size else '1280x800@60'))
        env=os.environ.copy();parent=Path(env['WAYLAND_DISPLAY'])
        if not parent.is_absolute():parent=Path(env['XDG_RUNTIME_DIR'])/parent
        env.update(XDG_RUNTIME_DIR=str(runtime),WAYLAND_DISPLAY=str(parent),HYPRLAND_NO_SD_VARS='1',
            HYPRLAND_PIXEL_DOOM_NESTED_ONLY='1',HYPRLAND_PIXEL_DOOM_BATCH_LIFECYCLE='1',
            HYPRLAND_PIXEL_DOOM_BATCH_MS='8',HYPRLAND_PIXEL_DOOM_FAST_ADDRESS='1',HYPRLAND_PIXEL_DOOM_BATCH_DRAW='1')
        env.pop('HYPRLAND_INSTANCE_SIGNATURE',None);env.pop('HYPRLAND_CMD',None)
        env.pop('HYPRLAND_PIXEL_DOOM_TEXTURE_CACHE',None)
        env.pop('HYPRLAND_PIXEL_DOOM_DEFER_TEXTURE',None)
        env.pop('HYPRLAND_PIXEL_DOOM_SKIP_UNCHANGED_RULES',None)
        env.pop('HYPRLAND_PIXEL_DOOM_COMBINED_GEOMETRY',None)
        env.pop('HYPRLAND_PIXEL_DOOM_FAST_FLOATING',None)
        if a.defer_texture:env['HYPRLAND_PIXEL_DOOM_DEFER_TEXTURE']='1'
        if a.skip_unchanged_rules:env['HYPRLAND_PIXEL_DOOM_SKIP_UNCHANGED_RULES']='1'
        if a.combined_geometry:env['HYPRLAND_PIXEL_DOOM_COMBINED_GEOMETRY']='1'
        if a.fast_floating:env['HYPRLAND_PIXEL_DOOM_FAST_FLOATING']='1'
        try:
            compositor=subprocess.Popen(['dbus-run-session','--',str(BINARY),'--config',str(config)],env=env,stdout=log,stderr=log,start_new_session=True)
            lock=wait_for(lambda:next(runtime.glob('hypr/*/hyprland.lock'),None))
            pid,display=lock.read_text().splitlines()[:2];ipc=lock.parent/'.socket.sock';wait_for(ipc.exists)
            errors=request(ipc,'configerrors').strip()
            if errors and errors!='ok':raise RuntimeError(errors)
            if fixed_size:
                parent_ipc=Path(os.environ['XDG_RUNTIME_DIR'])/'hypr'/os.environ['HYPRLAND_INSTANCE_SIGNATURE']/'.socket.sock'
                def find_host():
                    return next((w for w in json.loads(request(parent_ipc,'j/clients')) if w.get('pid')==int(pid)),None)
                host=wait_for(find_host)
                selector=json.dumps('address:'+host['address'])
                if a.host_workspace is not None:
                    request(parent_ipc,f'eval hl.dispatch(hl.dsp.window.move({{window={selector},workspace="{a.host_workspace}",follow=false}}))')
                    wait_for(lambda:(find_host() or {}).get('workspace',{}).get('id')==a.host_workspace)
                if a.record_parent:
                    for prop in ('opacity','opacity_inactive','opacity_fullscreen','opacity_override','opacity_inactive_override','opacity_fullscreen_override'):
                        request(parent_ipc,f'eval hl.dispatch(hl.dsp.window.set_prop({{window={selector},prop="{prop}",value="1"}}))')
                request(parent_ipc,f'eval hl.dispatch(hl.dsp.window.fullscreen({{window={selector},action="unset"}})); hl.dispatch(hl.dsp.window.float({{window={selector},action="on"}})); hl.dispatch(hl.dsp.window.resize({{window={selector},x={fixed_size[0]},y={fixed_size[1]}}}))')
                wait_for(lambda:(find_host() or {}).get('size')==fixed_size)
                wait_for(lambda:any([m['width'],m['height']]==fixed_size for m in json.loads(request(ipc,'j/monitors'))))
            child=env|{'PIXEL_DOOM_DISPOSABLE_SESSION':'1','WAYLAND_DISPLAY':str(runtime/display),'HYPRLAND_INSTANCE_SIGNATURE':lock.parent.name}
            if a.record_parent:
                if not fixed_size:p.error('--record-parent needs a fixed host size')
                host=find_host();x,y=host['at'];w,h=host['size']
                child.update(PIXEL_DOOM_CAPTURE_DISPLAY=str(parent),PIXEL_DOOM_CAPTURE_RUNTIME=os.environ['XDG_RUNTIME_DIR'],
                    PIXEL_DOOM_CAPTURE_GEOMETRY=f'{x},{y} {w}x{h}')
            if a.host_workspace is not None:
                child.update(PIXEL_DOOM_CAPTURE_WORKSPACE=str(a.host_workspace),PIXEL_DOOM_PARENT_IPC=str(parent_ipc))
                if a.focus_for_capture:child['PIXEL_DOOM_FOCUS_CAPTURE']='1'
            cmd=[sys.executable,str(ROOT/'progressive.py'),'--levels',str(a.levels),'--hold',str(a.hold),'--output',str(a.output)]
            cmd.extend(['--split-batch',str(a.split_batch),'--timeout',str(a.timeout)])
            cmd.extend(['--fps',str(a.fps)])
            if a.prestart_record:cmd.append('--prestart-record')
            if a.allow_slow:cmd.append('--allow-slow')
            if a.static_grid:cmd.append('--static-grid')
            if a.combined_geometry:cmd.append('--combined-geometry')
            if a.max_terminals is not None:cmd.extend(['--max-terminals',str(a.max_terminals)])
            if a.record:cmd.extend(['--record',str(a.output/'progressive.mp4')])
            initial_cpu=cpu_seconds(int(pid));last_cpu=initial_cpu;launch_started=time.monotonic()
            launcher=subprocess.Popen(cmd,env=child,start_new_session=True)
            deadline=time.monotonic()+a.timeout+120
            while launcher.poll() is None:
                if a.fixed_host_size:
                    try:last_cpu=cpu_seconds(int(pid))
                    except (FileNotFoundError,ProcessLookupError):pass
                if (a.output/'close-nested').exists() and compositor.poll() is None:
                    if a.fixed_host_size:
                        (a.output/'creation-cost.json').write_text(json.dumps(dict(
                            compositor_cpu_seconds_before_teardown=last_cpu-initial_cpu,
                            launcher_seconds_before_teardown=time.monotonic()-launch_started,
                            skip_unchanged_rules=a.skip_unchanged_rules,defer_texture=a.defer_texture,
                            terminal_cap=a.max_terminals,hold_seconds=a.hold),indent=2)+'\n')
                    os.killpg(compositor.pid,signal.SIGTERM)
                    try:compositor.wait(timeout=2)
                    except subprocess.TimeoutExpired:os.killpg(compositor.pid,signal.SIGKILL);compositor.wait()
                    # dbus-run-session can exit before Hyprland finishes its
                    # expensive teardown. Reap the entire disposable group.
                    try:os.killpg(compositor.pid,signal.SIGKILL)
                    except ProcessLookupError:pass
                if time.monotonic()>deadline:raise TimeoutError('Progressive session timeout')
                time.sleep(.1)
            if launcher.returncode:raise RuntimeError('Progressive preview failed')
            if a.record:
                video=a.output/'progressive.mp4'
                probe=subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(video)],capture_output=True,text=True)
                if probe.returncode or float(probe.stdout.strip() or 0)<a.hold-1:
                    raise RuntimeError('Recording missing or incomplete; do not use this stage as a video')
            print('Disposable nested session closed; terminal processes exited.',flush=True)
        finally:
            stop(launcher)
            # If the launcher had to be killed, also stop its isolated child group.
            if launcher:
                try:os.killpg(launcher.pid,signal.SIGTERM)
                except ProcessLookupError:pass
            if compositor and compositor.poll() is None:
                os.killpg(compositor.pid,signal.SIGTERM)
                try:compositor.wait(timeout=10)
                except subprocess.TimeoutExpired:os.killpg(compositor.pid,signal.SIGKILL);compositor.wait()
            if compositor:
                try:os.killpg(compositor.pid,signal.SIGKILL)
                except ProcessLookupError:pass
            # Foot may still be tearing down thousands of PTYs after the
            # launcher exits. All children share this private session group.
            if launcher:
                try:os.killpg(launcher.pid,signal.SIGKILL)
                except ProcessLookupError:pass
            for source in runtime.glob('hypr/*/hyprland.log'):(a.output/'hyprland.log').write_bytes(source.read_bytes())


if __name__=='__main__':main()

#!/usr/bin/env python3
"""Run the real DOOM launcher in a private nested compositor, capped at 3072 cells."""
import argparse
import json
import os
import re
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import threading
import statistics

from benchmark_lifecycle import request, wait_for, stop

ROOT = Path(__file__).resolve().parent
BINARY = Path('/tmp/pixel-doom-hyprland-build/Hyprland')
FOOT = Path('/tmp/pixel-doom-foot-build/foot')


def trial(cols, rows, diagnostic, repeat, seconds, fps, out, spawn_delay=.01, profile=False, presentation_sample=None, intro=False, cache_geometry=False, batch_draw=False, monitor_damage=False, texture_cache=False, defer_texture=False, skip_unchanged_rules=False):
    label = f'launcher-{cols*rows}-font-{"on" if diagnostic else "off"}-{repeat}'
    summary = dict(label=label, status='failed',batch_draw=batch_draw,monitor_damage=monitor_damage,texture_cache=texture_cache,defer_texture=defer_texture)
    summary['skip_unchanged_rules']=skip_unchanged_rules
    compositor = launcher = sampler = None
    host_samples=[]
    host_stop=threading.Event()
    host_thread=None
    parent_ipc=Path(os.environ['XDG_RUNTIME_DIR'])/'hypr'/os.environ['HYPRLAND_INSTANCE_SIGNATURE']/'.socket.sock'
    def watch_host(pid):
        while not host_stop.is_set():
            try:
                clients=json.loads(request(parent_ipc,'j/clients'))
                monitors=json.loads(request(parent_ipc,'j/monitors'))
                hosts=[w for w in clients if w.get('pid')==pid]
                active={m['activeWorkspace']['id'] for m in monitors if m.get('dpmsStatus',True)}
                host_samples.append(dict(time=time.monotonic(),visible=any(w['workspace']['id'] in active and not w.get('hidden',False) for w in hosts),
                    windows=[{k:w.get(k) for k in ('address','workspace','hidden','fullscreen','size')} for w in hosts]))
            except (OSError,ValueError) as e:
                host_samples.append(dict(time=time.monotonic(),error=str(e)))
            host_stop.wait(1)

    with tempfile.TemporaryDirectory(prefix='pdl-') as directory:
        tmp = Path(directory)
        runtime = tmp / 'r'
        runtime.mkdir(mode=0o700)
        config = tmp / 'hyprland.lua'
        config.write_text('''hl.monitor({output="",mode="800x600@60",position="auto",scale=1})
hl.config({animations={enabled=false},general={border_size=0,gaps_in=0,gaps_out=0},
 decoration={rounding=0,blur={enabled=false},shadow={enabled=false}},
 misc={disable_hyprland_logo=true,disable_splash_rendering=true,disable_watchdog_warning=true},
 debug={disable_logs=false}})
''' + ('hl.config({debug={damage_tracking=1}})\n' if monitor_damage else ''))
        env = os.environ.copy()
        parent = Path(env['WAYLAND_DISPLAY'])
        if not parent.is_absolute():
            parent = Path(env['XDG_RUNTIME_DIR']) / parent
        env.update(XDG_RUNTIME_DIR=str(runtime),WAYLAND_DISPLAY=str(parent),HYPRLAND_NO_SD_VARS='1',
            HYPRLAND_PIXEL_DOOM_NESTED_ONLY='1',HYPRLAND_PIXEL_DOOM_BATCH_LIFECYCLE='1',
            HYPRLAND_PIXEL_DOOM_BATCH_MS='8',HYPRLAND_PIXEL_DOOM_FAST_ADDRESS='1')
        env.pop('HYPRLAND_INSTANCE_SIGNATURE',None)
        env.pop('HYPRLAND_CMD',None)
        env.pop('HYPRLAND_PIXEL_DOOM_BATCH_DRAW',None)
        env.pop('HYPRLAND_PIXEL_DOOM_TEXTURE_CACHE',None)
        env.pop('HYPRLAND_PIXEL_DOOM_DEFER_TEXTURE',None)
        env.pop('HYPRLAND_PIXEL_DOOM_SKIP_UNCHANGED_RULES',None)
        if batch_draw: env['HYPRLAND_PIXEL_DOOM_BATCH_DRAW']='1'
        if texture_cache: env['HYPRLAND_PIXEL_DOOM_TEXTURE_CACHE']='1'
        if defer_texture: env['HYPRLAND_PIXEL_DOOM_DEFER_TEXTURE']='1'
        if skip_unchanged_rules: env['HYPRLAND_PIXEL_DOOM_SKIP_UNCHANGED_RULES']='1'
        with (out/f'{label}-compositor.log').open('w') as comp_log, (out/f'{label}.log').open('w') as log:
            try:
                compositor = subprocess.Popen(['dbus-run-session','--',str(BINARY),'--config',str(config)],
                    env=env,stdout=comp_log,stderr=comp_log,start_new_session=True)
                def ipc_ready():
                    if compositor.poll() is not None:
                        raise RuntimeError('Nested compositor exited')
                    return next(runtime.glob('hypr/*/hyprland.lock'),None)
                lock = wait_for(ipc_ready)
                pid, display = lock.read_text().splitlines()[:2]
                ipc = lock.parent/'.socket.sock'
                wait_for(lambda: ipc.exists())
                errors = request(ipc,'configerrors').strip()
                if errors and errors!='ok':
                    raise RuntimeError(errors)
                # Tiled host dimensions vary with the user's other windows.
                # Fix only this disposable host's size for matched comparisons.
                def find_host():
                    return next((w for w in json.loads(request(parent_ipc,'j/clients')) if w.get('pid')==int(pid)),None)
                host=wait_for(find_host)
                selector=json.dumps('address:'+host['address'])
                request(parent_ipc,f'eval hl.dispatch(hl.dsp.window.float({{window={selector},action="on"}})); hl.dispatch(hl.dsp.window.resize({{window={selector},x=800,y=600}}))')
                wait_for(lambda: (find_host() or {}).get('size')==[800,600])
                child_env = env | {'WAYLAND_DISPLAY':str(runtime/display),
                                   'HYPRLAND_INSTANCE_SIGNATURE':lock.parent.name}
                metrics = out/f'{label}.json'
                cmd = [sys.executable,str(ROOT/'run.py'),'--cols',str(cols),'--rows',str(rows),
                    '--seconds',str(seconds),'--fps',str(fps),'--gap','0','--server-size','128',
                    '--placement-batch','4','--startup-timeout','120','--min-free-gib','8',
                    '--spawn-delay',str(spawn_delay),
                    '--foot-binary',str(FOOT),'--single-pixel-buffers','--metrics',str(metrics)]
                if batch_draw:
                    subprocess.run([sys.executable,str(ROOT/'verify_batch_draw.py'),str(out/'verification')],env=child_env,stdout=log,stderr=log,timeout=25,check=True)
                if cache_geometry:
                    subprocess.run([sys.executable,str(ROOT/'test_single_pixel.py'),'--cache-pixel-geometry'],env=child_env,stdout=log,stderr=log,timeout=20,check=True)
                    cmd.append('--cache-pixel-geometry')
                if intro:
                    cmd.append('--intro')
                if presentation_sample is not None:
                    cmd.extend(['--presentation-sample',str(presentation_sample)])
                if diagnostic:
                    cmd.append('--font-monospace-check')
                if profile:
                    from cpu_sample import Sampler
                    sampler = Sampler(int(pid))
                started = time.monotonic()
                summary["launcher_started_monotonic"] = started
                host_thread=threading.Thread(target=watch_host,args=(int(pid),),daemon=True)
                host_thread.start()
                launcher = subprocess.Popen(cmd,env=child_env,stdout=log,stderr=log,start_new_session=True)
                if intro:
                    for delay,name in ((2,'identity'),(5.5,'population')):
                        time.sleep(max(0,started+delay-time.monotonic()))
                        if launcher.poll() is None:
                            subprocess.run(['grim',str(out/f'{label}-intro-{name}.png')],env=child_env,stdout=log,stderr=log,timeout=10,check=True)
                code = launcher.wait(timeout=180)
                summary['total_seconds'] = time.monotonic()-started
                summary['launcher_exit'] = code
                if code:
                    raise RuntimeError(f'Launcher exited {code}; see log')
                report = json.loads(metrics.read_text())
                if report.get('compositor_pids') != [int(pid)] or report.get('compositor_scope')!='ipc-instance':
                    raise RuntimeError('Compositor CPU was not scoped to the nested instance')
                if report['geometry_mismatches']:
                    raise RuntimeError('Geometry mismatch')
                if report['sample_seconds'] < seconds-.5 or not all(s['demo_visible'] for s in report['compositor_samples']):
                    raise RuntimeError('Playback ended early or nested workspace changed')
                play_start=report.get('playback_started_monotonic',started+report['startup_seconds'])
                playback_host=[v for v in host_samples if play_start<=v['time']<=play_start+report['sample_seconds']]
                summary['host_visible_during_playback']=bool(playback_host) and all(v.get('visible',False) for v in playback_host)
                if not summary['host_visible_during_playback']:
                    raise RuntimeError('Nested host was hidden or could not be observed during playback')
                summary['host_sizes']=sorted({tuple(w['size']) for v in playback_host for w in v.get('windows',[])})
                if summary['host_sizes']!=[(800,600)]:raise RuntimeError('Host size changed during comparison')
                if presentation_sample is not None:
                    feedback=re.findall(r'PD_PRESENT time_ns=(\d+) latency_us=(\d+)',metrics.with_suffix('.foot.log').read_text())
                    play_start=report.get('playback_started_monotonic',started+report['startup_seconds'])
                    play_end=play_start+report['sample_seconds']
                    presented=[(int(stamp)/1e9,int(latency)/1000) for stamp,latency in feedback
                               if play_start+.5<=int(stamp)/1e9<=play_end+.5]
                    summary['presentation_feedback_count']=len(presented)
                    if (len(presented)<10 or presented[0][0]>play_start+3 or presented[-1][0]<play_end-3
                        or any(b[0]-a[0]>3 for a,b in zip(presented,presented[1:]))):
                        raise RuntimeError('Insufficient sustained presentation feedback; playback result is invalid')
                    summary['presentation_latency_median_ms']=statistics.median(v[1] for v in presented)
                    summary['presentation_interval_median_ms']=statistics.median((b[0]-a[0])*1000 for a,b in zip(presented,presented[1:]))
                wait_for(lambda: not json.loads(request(ipc,'j/clients')))
                summary.update(status='complete',remaining_windows=0,startup_seconds=report['startup_seconds'],
                               sample_seconds=report['sample_seconds'],geometry_mismatches=report['geometry_mismatches'])
            except Exception as error:
                summary['error']=str(error)
            finally:
                host_stop.set()
                if host_thread: host_thread.join(timeout=16)
                (out/f'{label}-host-visibility.json').write_text(json.dumps(host_samples,indent=2)+'\n')
                stop(launcher)
                if sampler is not None:
                    (out/f'{label}-profile.json').write_text(json.dumps(sampler.finish())+'\n')
                if compositor is not None and compositor.poll() is None:
                    os.killpg(compositor.pid,signal.SIGTERM)
                    try:
                        compositor.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        os.killpg(compositor.pid,signal.SIGKILL)
                        compositor.wait(timeout=5)
                for source in runtime.glob('hypr/*/hyprland.log'):
                    (out/f'{label}-hyprland.log').write_bytes(source.read_bytes())
    (out/f'{label}-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    return summary


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--optimized-only',action='store_true')
    p.add_argument('--batch-draw',action='store_true')
    p.add_argument('--texture-cache',action='store_true')
    p.add_argument('--defer-texture',action='store_true')
    p.add_argument('--skip-unchanged-rules',action='store_true')
    p.add_argument('--monitor-damage',action='store_true',help='Redraw full nested monitor on damaged frames')
    p.add_argument('--cache-pixel-geometry',action='store_true')
    p.add_argument('--intro',action='store_true')
    p.add_argument('--presentation-sample',type=int)
    p.add_argument('--profile',action='store_true')
    p.add_argument('--spawn-delay',type=float,default=.01)
    p.add_argument('--output',type=Path,default=ROOT/'output'/'launcher-validation')
    p.add_argument('--cols',type=int,default=32)
    p.add_argument('--rows',type=int,default=32)
    p.add_argument('--seconds',type=int,default=8)
    p.add_argument('--fps',type=int,default=15)
    p.add_argument('--repeats',type=int,default=2)
    args=p.parse_args()
    if args.texture_cache and not args.batch_draw:p.error('--texture-cache requires --batch-draw')
    if args.defer_texture and (not args.batch_draw or args.texture_cache):p.error('--defer-texture requires --batch-draw and no --texture-cache')
    if not (4<=args.cols<=64 and 4<=args.rows<=64 and args.cols*args.rows<=3072 and 4<=args.seconds<=45 and 1<=args.fps<=35 and 1<=args.repeats<=2 and 0<=args.spawn_delay<=.05):
        p.error('Bounded to 3072 cells, 4–45 seconds, 1–35 FPS, and 1–2 pairs')
    binary=BINARY.read_bytes()
    guards=[b'HYPRLAND_PIXEL_DOOM_NESTED_ONLY',b'HYPRLAND_PIXEL_DOOM_FAST_ADDRESS']
    if args.batch_draw: guards.append(b'HYPRLAND_PIXEL_DOOM_BATCH_DRAW')
    if args.defer_texture: guards.append(b'HYPRLAND_PIXEL_DOOM_DEFER_TEXTURE')
    if args.skip_unchanged_rules: guards.append(b'HYPRLAND_PIXEL_DOOM_SKIP_UNCHANGED_RULES')
    if args.texture_cache: guards.append(b'HYPRLAND_PIXEL_DOOM_TEXTURE_CACHE')
    for guard in guards:
        if guard not in binary:
            p.error('Required private compositor patch is missing')
    out=args.output.resolve()
    out.mkdir(parents=True,exist_ok=True)
    results=[]
    for repeat in range(args.repeats):
        for diagnostic in ([False] if args.optimized_only else ([True,False] if repeat%2==0 else [False,True])):
            result=trial(args.cols,args.rows,diagnostic,repeat,args.seconds,args.fps,out,args.spawn_delay,args.profile,args.presentation_sample,args.intro,args.cache_pixel_geometry,args.batch_draw,args.monitor_damage,args.texture_cache,args.defer_texture,args.skip_unchanged_rules)
            results.append(result)
            print(json.dumps(result),flush=True)
            if result['status']!='complete':
                raise SystemExit(1)
    (out/f'comparison-{args.cols*args.rows}.json').write_text(json.dumps(results,indent=2)+'\n')


if __name__=='__main__':
    main()

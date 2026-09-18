#!/usr/bin/env python3
"""Experimental real-terminal DOOM mosaic. Q quits; all windows are temporary."""
import argparse
import json
import os
from pathlib import Path
import re
import signal
import socket
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from hyprsplitter import Hyprland
from foot_ipc import open_window


def build(source, output, extra_cflags=()):
    files = re.findall(r'"(src/doomgeneric/[^"\n]+\.c)"', (source / 'build.zig').read_text())
    inputs = [Path(__file__).with_name('bridge.c'), source/'build.zig',
              *[source/f for f in files], *list((source/'src/doomgeneric').glob('*.h'))]
    if output.exists() and output.stat().st_mtime > max(f.stat().st_mtime for f in inputs):
        return
    staged = output.with_name(output.name+f'.{os.getpid()}')
    subprocess.run(['gcc', '-std=gnu11', '-O2', '-w', *extra_cflags, '-DDOOMGENERIC_RESX=320', '-DDOOMGENERIC_RESY=200',
                    '-I'+str(source/'src/doomgeneric'), str(Path(__file__).with_name('bridge.c')),
                    *[str(source/f) for f in files], '-lm', '-o', str(staged)], check=True)
    staged.replace(output)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--cols', type=int, default=80)
    p.add_argument('--rows', type=int, default=64)
    p.add_argument('--seconds', type=float, default=0, help='Automatically close after this many seconds')
    p.add_argument('--intro', action='store_true', help='Show real terminal identities and a live count during creation; recordings include the intro')
    p.add_argument('--play', action='store_true', help='Start a playable game instead of the recorded DOOM demo')
    p.add_argument('--source', type=Path, default=Path.home()/'Projects/terminal-doom')
    p.add_argument('--build-only', action='store_true')
    p.add_argument('--capture', type=Path, help='Save a screenshot of the grid after it starts')
    p.add_argument('--capture-delay', type=float, default=4, help='Seconds before taking the screenshot')
    p.add_argument('--record', type=Path, help='Record 20 seconds of gameplay as an MP4')
    p.add_argument('--record-delay', type=float, default=30, help='Warm-up seconds before recording')
    p.add_argument('--metrics', type=Path, help='Save startup time, process/thread counts and CPU usage')
    p.add_argument('--renderer', choices=['hub','process'], default='hub')
    p.add_argument('--foot-binary', default='foot', help='Alternate experimental Foot executable')
    p.add_argument('--font-monospace-check', action='store_true', help='Restore the per-window font diagnostic; disabled for the fixed experiment font')
    p.add_argument('--single-pixel-buffers', action='store_true', help='Enable opt-in path in the patched Foot build')
    p.add_argument('--cache-pixel-geometry', action='store_true', help='Avoid redundant viewport requests in the private Foot build')
    p.add_argument('--presentation-sample', type=int, help='Pixel index whose presentation feedback is logged by the private Foot build')
    p.add_argument('--color-buffer-cache', action='store_true', help='Use exact-color protocol buffer cache in patched Foot (requires --single-pixel-buffers)')
    p.add_argument('--no-pixel-frame-callback', action='store_true', help='Experimental externally paced blank-terminal rendering')
    p.add_argument('--ipc', choices=['auto','cli'], default='auto')
    p.add_argument('--fps', type=int, default=15)
    p.add_argument('--gap', type=int, default=2)
    p.add_argument('--limit-windows', type=int, help='Only open this many cells, for layout probes')
    p.add_argument('--startup-timeout', type=float, default=600, help='Stop opening windows after this many seconds')
    p.add_argument('--min-free-gib', type=float, default=4, help='Stop opening windows below this available-memory reserve')
    p.add_argument('--freeze-after', type=float, help='Freeze DOOM after N seconds to compare static window cost')
    p.add_argument('--batch-pause', type=float, default=0.1, help='Let desktop event queues settle between window batches')
    p.add_argument('--batch-size', type=int, default=64, help='Windows per placement batch')
    p.add_argument('--server-size', type=int, default=640, help='Maximum pixel windows per Foot server (1–640)')
    p.add_argument('--paced-cleanup', action=argparse.BooleanOptionalAction, default=True, help='Wait for each server window group to disappear before stopping the next')
    p.add_argument('--initial-size-rule', action=argparse.BooleanOptionalAction, default=True, help='Set tiny initial window dimensions before mapping')
    p.add_argument('--placement-batch', type=int, default=16, help='Window moves per compositor request')
    p.add_argument('--spawn-delay', type=float, default=0.01, help='Seconds between individual window launches')
    p.add_argument('--setup-without-shell', action='store_true', help='Temporarily stop Omarchy shell during creation; restore before gameplay')
    a = p.parse_args()
    if not (4 <= a.cols <= 320 and 4 <= a.rows <= 200):
        p.error('Use 4–320 columns and 4–200 rows')
    if not (1<=a.fps<=35 and 0<=a.gap<=4): p.error('FPS: 1–35; gap: 0–4')
    if a.limit_windows is not None and a.limit_windows<1: p.error('Window limit must be positive')
    if a.startup_timeout<=0 or a.min_free_gib<0: p.error('Startup timeout must be positive; memory reserve cannot be negative')
    if a.batch_pause<0 or a.spawn_delay<0: p.error('Launch pauses cannot be negative')
    if not 1<=a.batch_size<=128: p.error('Batch size must be 1–128')
    if not 1<=a.placement_batch<=16: p.error('Placement batch must be 1–16')
    if a.color_buffer_cache and not a.single_pixel_buffers: p.error('Color cache requires --single-pixel-buffers')
    if a.no_pixel_frame_callback and not a.single_pixel_buffers: p.error('Callback experiment requires --single-pixel-buffers')
    if not 1<=a.server_size<=640: p.error('Server size must be 1–640')
    count=min(a.limit_windows or a.cols*a.rows,a.cols*a.rows)
    if a.presentation_sample is not None and (not a.single_pixel_buffers or not 0<=a.presentation_sample<count):
        p.error('Presentation sample requires patched single-pixel rendering and an existing pixel index')
    for output in (a.record,a.capture,a.metrics):
        if output: output.parent.mkdir(parents=True,exist_ok=True)
    binary = Path('/tmp/hyprsplitter-pixel-doom-bridge')
    build(a.source, binary)
    hub_binary=Path('/tmp/pixel-doom-hub')
    hub_source=Path(__file__).with_name('hub.c')
    if not hub_binary.exists() or hub_source.stat().st_mtime>hub_binary.stat().st_mtime:
        subprocess.run(['gcc','-std=gnu11','-O2','-Wall','-Wextra',str(hub_source),'-o',str(hub_binary)],check=True)
    if a.build_only:
        print(binary); return
    pty_limit=int(Path('/proc/sys/kernel/pty/max').read_text())
    pty_used=int(Path('/proc/sys/kernel/pty/nr').read_text())
    if count+1 > pty_limit-pty_used:
        p.error(f'This grid needs {count+1} free pseudo-terminals, but only '
                f'{pty_limit-pty_used} remain (kernel.pty.max={pty_limit}). '
                'Use --cols 64 --rows 40, or temporarily raise kernel.pty.max.')
    setup_started=time.monotonic()
    h = Hyprland()
    # Attribute CPU to this IPC instance, including when running nested.
    try:
        compositor_pid=int((Path(h.path).parent/'hyprland.lock').read_text().splitlines()[0])
        if read_comm(Path(f'/proc/{compositor_pid}')) != 'Hyprland':
            raise ValueError('Compositor PID is not live')
        compositor_pids=[compositor_pid]
        compositor_scope='ipc-instance'
    except (OSError, ValueError, IndexError):
        compositor_pids=[int(path.name) for path in Path('/proc').iterdir()
                         if path.name.isdigit() and read_comm(path)=='Hyprland']
        compositor_scope='all-Hyprland-fallback'

    shell_pids=[int(path.name) for path in Path('/proc').iterdir()
               if path.name.isdigit() and read_comm(path)=='quickshell']
    previous = h.request('activeworkspace', True)['name']
    previous_window = h.request('activewindow', True).get('address')
    monitor = next(m for m in h.request('monitors', True) if m['focused'])
    occupied = {w['id'] for w in h.request('workspaces', True)}
    workspace = next(i for i in range(90, 10000) if i not in occupied)
    app = f'pixel-doom-{os.getpid()}'
    rule = f'pixel_doom_{os.getpid()}'
    width, height = int(monitor['width']/monitor['scale']), int(monitor['height']/monitor['scale'])
    # Keep visible separation between the actual terminal windows.
    grid_width=min(width-60,int((height-100)*1.6))
    grid_height=int(grid_width/1.6)
    cell_w, cell_h = grid_width//a.cols, grid_height//a.rows
    if min(cell_w,cell_h)<=a.gap: p.error('Cells too small; reduce --gap')
    x0, y0 = (width-cell_w*a.cols)//2, (height-cell_h*a.rows)//2+12
    procs, installed, recorder = [], False, None
    intro=None; recording_started=None
    servers=[]; hubs=[]
    opened=0; startup_samples=[]; shell_stopped=False
    def stop(*_):
        raise KeyboardInterrupt
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    with tempfile.TemporaryDirectory(prefix='pixel-doom-') as temp:
        tmp=Path(temp)
        frames=tmp/'frame.rgb'
        if a.intro:
            # A visible checkerboard makes each newly opened real window apparent.
            palette=(bytes((14,48,62)),bytes((24,104,124)))
            frames.write_bytes(b''.join(palette[(i%a.cols+i//a.cols)%2] for i in range(a.cols*a.rows)))
        else:
            frames.write_bytes(bytes(a.cols*a.rows*3))
        keys=socket.socket(socket.AF_UNIX,socket.SOCK_DGRAM)
        keys.bind(str(tmp/'keys')); keys.setblocking(False)
        log=open(tmp/'foot.log','w')
        try:
            if a.setup_without_shell:
                if subprocess.run(['omarchy-hyprland-session-locked']).returncode!=1:
                    raise RuntimeError('Cannot stop shell while session is locked or lock state is unknown')
                shell_stopped=True
                subprocess.run(['quickshell','kill','-p','/usr/share/omarchy/shell'],
                               check=True,timeout=10,stdout=log,stderr=log)
            size_rule=f'size={{{cell_w-a.gap},{cell_h-a.gap}}}, ' if a.initial_size_rule else ''
            h.request(f'eval {rule}=hl.window_rule({{name="{rule}", match={{class="^{app}$"}}, '
                      f'workspace="{workspace} silent", float=true, no_anim=true, no_initial_focus=true, {size_rule}'
                      'border_size=0, rounding=0, no_shadow=true, no_blur=true, '
                      'opacity="1 override 1 override"})')
            installed=True
            # Bound each Wayland event loop's load; a single server stalls at
            # thousands of independently changing terminal surfaces.
            servers=[]; server_sockets=[]; hubs=[]; hub_sockets=[]
            direct=a.ipc=='auto' and subprocess.check_output([a.foot_binary,'--version'],text=True).startswith('foot version: 1.28.')
            def create(server,title,w,h,command):
                if direct:
                    open_window(server,app,title,w,h,command,a.renderer=='hub')
                else:
                    subprocess.run(['footclient','-s',str(server),'-N',
                        *(['-H'] if a.renderer=='hub' else []),'-a',app,'-T',title,'-w',f'{w}x{h}',
                        *map(str,command)],check=True,stdout=log,stderr=log)
            for group in range((count+a.server_size-1)//a.server_size):
                server_socket=tmp/f'foot-{group}.sock'
                foot_env=os.environ.copy()
                foot_env.pop('FOOT_PIXEL_DOOM',None)
                if a.single_pixel_buffers: foot_env['FOOT_PIXEL_DOOM']='1'
                foot_env.pop('FOOT_PIXEL_DOOM_CACHE',None)
                if a.color_buffer_cache: foot_env['FOOT_PIXEL_DOOM_CACHE']='1'
                foot_env.pop('FOOT_PIXEL_DOOM_NO_CALLBACK',None)
                if a.no_pixel_frame_callback: foot_env['FOOT_PIXEL_DOOM_NO_CALLBACK']='1'
                foot_env.pop('FOOT_PIXEL_DOOM_CACHE_GEOMETRY',None)
                if a.cache_pixel_geometry: foot_env['FOOT_PIXEL_DOOM_CACHE_GEOMETRY']='1'
                foot_env.pop('FOOT_PIXEL_DOOM_SAMPLE_TITLE',None)
                sample_this_server=a.presentation_sample is not None and a.presentation_sample//a.server_size==group
                if sample_this_server: foot_env['FOOT_PIXEL_DOOM_SAMPLE_TITLE']=f'{app}-{a.presentation_sample}'
                server=subprocess.Popen([a.foot_binary,*(['--presentation-timings'] if sample_this_server else []),'--config=/dev/null','--server='+str(server_socket),
                    '-o',('font=monospace:pixelsize=1' if min(cell_w,cell_h)<8 else 'font=monospace:size=2'),
                    '-o','pad=0x0','-o','resize-by-cells=no',
                    '-o','workers=0','-o','scrollback.lines=0',
                    *([] if a.font_monospace_check else ['-o','tweak.font-monospace-warn=no']),
                    '-o','colors-dark.background=080808'],stdout=log,stderr=log,
                    start_new_session=True,env=foot_env)
                procs.append(server); servers.append(server); server_sockets.append(server_socket)
                deadline=time.monotonic()+5
                while not server_socket.exists():
                    if server.poll() is not None or time.monotonic()>deadline:
                        log.flush(); raise RuntimeError((tmp/'foot.log').read_text())
                    time.sleep(.05)
                hub_socket=tmp/f'hub-{group}.sock'; hub_sockets.append(hub_socket)
                if a.renderer=='hub':
                    hub=subprocess.Popen([str(hub_binary),str(frames),str(hub_socket),str(tmp/'keys'),
                                          str(a.server_size+1),str(a.fps)],stdout=log,stderr=log)
                    hubs.append(hub); procs.append(hub)
                    deadline=time.monotonic()+5
                    while not hub_socket.exists():
                        if hub.poll() is not None or time.monotonic()>deadline: raise RuntimeError('Hub failed to start')
                        time.sleep(.01)
            # A real black terminal behind the mosaic hides the wallpaper in gaps.
            backdrop=tmp/'backdrop.rgb'; backdrop.write_bytes(bytes(3))
            create(server_sockets[0],f'{app}-backdrop',width,height,
                   [hub_binary,'attach',hub_sockets[0],'-1'] if a.renderer=='hub' else
                   [binary,'pixel',backdrop,'0',tmp/'keys',str(a.fps)])
            deadline=time.monotonic()+10
            while True:
                backgrounds=[w for w in h.request('clients',True) if w['title']==f'{app}-backdrop']
                if backgrounds: break
                if time.monotonic()>deadline: raise RuntimeError('Backdrop did not open')
                time.sleep(.05)
            selector=json.dumps('address:'+backgrounds[0]['address'])
            h.run(f'hl.dsp.window.resize({{window={selector},x={width},y={height}}})',
                  f'hl.dsp.window.move({{window={selector},x={monitor["x"]},y={monitor["y"]}}})')
            if a.intro:
                h.run(f'hl.dsp.focus({{workspace="{workspace}"}})')
                if a.record:
                    recorder=subprocess.Popen(['gpu-screen-recorder','-w',monitor['name'],
                        '-k','h264','-f',str(max(30,a.fps)),'-fm','cfr','-fallback-cpu-encoding','yes',
                        '-o',str(a.record)],stdout=log,stderr=log)
                    recording_started=time.monotonic()
                from intro import Intro
                intro=Intro(h,a.foot_binary,tmp,workspace,monitor,app,count,log,procs)
            placed=set()
            for i in range(count):
                if i%a.batch_size==0:
                    available=int(re.search(r'MemAvailable:\s+(\d+)',Path('/proc/meminfo').read_text())[1])/1048576
                    elapsed=time.monotonic()-setup_started
                    if available<a.min_free_gib or elapsed>a.startup_timeout:
                        if a.metrics:
                            a.metrics.write_text(json.dumps({'status':'startup_stopped','opened':i,
                                'requested':count,'available_gib':round(available,2),
                                'startup_seconds':round(elapsed,3)},indent=2)+'\n')
                        raise RuntimeError(f'Stopped at {i}/{count} terminals: {available:.1f} GiB available, '
                                           f'{elapsed:.0f}s startup; reached memory reserve or time limit')
                create(server_sockets[i//a.server_size],f'{app}-{i}',cell_w-a.gap,cell_h-a.gap,
                       [hub_binary,'attach',hub_sockets[i//a.server_size],str(i)] if a.renderer=='hub' else
                       [binary,'pixel',frames,str(i),tmp/'keys',str(a.fps)])
                opened=i+1
                time.sleep(a.spawn_delay)
                if (i+1)%a.batch_size==0 or i==count-1:
                    placement=place(h,app,placed,a.cols,cell_w,cell_h,x0+monitor['x'],y0+monitor['y'],a.gap,a.placement_batch)
                    time.sleep(a.batch_pause)
                    ping=time.monotonic(); h.request('activeworkspace',True)
                    latency=time.monotonic()-ping
                    startup_samples.append({'opened':opened,'ipc_ms':round(latency*1000,2),**placement})
                    if intro:
                        actual=sum(w['class']==app and not w['title'].endswith('-backdrop') for w in h.request('clients',True))
                        intro.update(actual,compact=True)
                    if latency>.25:
                        raise RuntimeError('Stopping startup: compositor response exceeded 250ms')
                if (i+1)%256==0:
                    print(f'Opening terminals: {i+1}/{count}',flush=True)
            deadline=time.monotonic()+10
            while len(placed)<count and time.monotonic()<deadline:
                place(h,app,placed,a.cols,cell_w,cell_h,x0+monitor['x'],y0+monitor['y'],a.gap,a.placement_batch); time.sleep(.1)
            if len(placed)!=count:
                raise RuntimeError(f'Only {len(placed)} windows appeared')
            if shell_stopped:
                subprocess.run(['omarchy','restart','shell'],check=True,timeout=30,stdout=log,stderr=log)
                shell_stopped=False
                shell_pids=[int(path.name) for path in Path('/proc').iterdir()
                            if path.name.isdigit() and read_comm(path)=='quickshell']
            clients=[w for w in h.request('clients',True)
                     if w['class']==app and not w['title'].endswith('-backdrop')]
            mismatched=sum(w['size']!=[cell_w-a.gap,cell_h-a.gap] for w in clients)
            if mismatched: print(f'NOTE: {mismatched} windows have compositor-constrained dimensions',flush=True)
            h.run(f'hl.dsp.focus({{workspace="{workspace}"}})')
            if intro:
                intro.finish(len(clients)); intro=None
            h.focus(clients[len(clients)//2]['address'])
            doomlog=open('/tmp/hyprsplitter-pixel-doom-engine.log','w')
            engine_command=[str(binary),str(frames),str(a.cols),str(a.rows),
                '-iwad',str(a.source/'doom1.wad'),'-config',str(tmp/'doom.cfg'),
                '-nosound',*(['-warp','1','1'] if a.play else ['-playdemo','demo1'])]
            engine_env={**os.environ,'PIXEL_DOOM_OUTPUT_FPS':str(a.fps)}
            engine=subprocess.Popen(engine_command,
                cwd=tmp,stdin=subprocess.PIPE,stdout=doomlog,stderr=doomlog,env=engine_env)
            procs.append(engine)
            metric_pids=[os.getpid(),engine.pid,*[hub.pid for hub in hubs]]
            for server in servers:
                metric_pids.append(server.pid)
                children=Path(f'/proc/{server.pid}/task/{server.pid}/children')
                metric_pids.extend(int(pid) for pid in children.read_text().split())
            metric_roles={os.getpid():'launcher',engine.pid:'doom',
                          **{hub.pid:f'hub-{i}' for i,hub in enumerate(hubs)},
                          **{server.pid:f'foot-{i}' for i,server in enumerate(servers)}}
            initial_by_pid={pid:process_usage([pid]) for pid in set(metric_pids)}
            initial_usage=process_usage(metric_pids)
            startup_seconds=time.monotonic()-setup_started
            print(f'LIVE: {len(placed)} actual terminals on workspace {workspace}. Q quits. '+
                  ('W/S move, A/D turn, F fire, Space use.' if a.play else 'Playing the original DOOM demo.'),flush=True)
            started=time.monotonic(); held={}; captured=False
            frozen=False; samples=[]; last_sample=started; slow_samples=0
            last_compositor=process_usage(compositor_pids)['cpu_seconds']
            last_shell=process_usage(shell_pids)['cpu_seconds']
            last_by_pid={pid:usage['cpu_seconds'] for pid,usage in initial_by_pid.items()}
            while not a.seconds or time.monotonic()-started<a.seconds:
                now=time.monotonic()
                if a.freeze_after is not None and not frozen and now-started>=a.freeze_after:
                    engine.send_signal(signal.SIGSTOP); frozen=True
                if now-last_sample>=1:
                    cpu=process_usage(compositor_pids)['cpu_seconds']
                    shell_cpu=process_usage(shell_pids)['cpu_seconds']
                    process_cores={}
                    for pid,previous_cpu in last_by_pid.items():
                        current_cpu=process_usage([pid])['cpu_seconds']
                        process_cores[metric_roles.get(pid,f'child-{pid}')]=round(
                            max(0,current_cpu-previous_cpu)/(now-last_sample),4)
                        last_by_pid[pid]=current_cpu
                    ping=time.monotonic()
                    visible=None
                    try: visible=h.request('activeworkspace',True)['id']==workspace
                    except TimeoutError: pass
                    latency=time.monotonic()-ping
                    samples.append({'seconds':round(now-started,2),'frozen':frozen,
                                    'demo_visible':visible,'process_cores':process_cores,
                                    'hyprland_cores':round((cpu-last_compositor)/(now-last_sample),3),
                                    'shell_cores':round((shell_cpu-last_shell)/(now-last_sample),3),
                                    'ipc_ms':round(latency*1000,2)})
                    last_compositor=cpu; last_shell=shell_cpu; last_sample=now
                    slow_samples=slow_samples+1 if latency>.25 else 0
                    if slow_samples>=2:
                        print('Stopping: compositor IPC exceeded 250ms twice',flush=True); break
                if engine.poll() is not None:
                    if a.play or engine.returncode:
                        raise RuntimeError('DOOM exited; see /tmp/hyprsplitter-pixel-doom-engine.log')
                    engine.stdin.close(); procs.remove(engine)
                    engine=subprocess.Popen(engine_command,cwd=tmp,stdin=subprocess.PIPE,
                                            stdout=doomlog,stderr=doomlog,env=engine_env)
                    procs.append(engine); held.clear()
                if any(proc.poll() is not None for proc in [*servers,*hubs]): raise RuntimeError('Terminal server or hub exited')
                if (a.record and recording_started is None and time.monotonic()-started>a.record_delay
                        and any(frames.read_bytes())):
                    h.run(f'hl.dsp.focus({{workspace="{workspace}"}})')
                    time.sleep(.3)
                    recorder=subprocess.Popen(['gpu-screen-recorder','-w',monitor['name'],
                        '-k','h264','-f',str(max(30,a.fps)),'-fm','cfr','-fallback-cpu-encoding','yes',
                        '-o',str(a.record)],stdout=log,stderr=log)
                    recording_started=time.monotonic()
                if recorder and time.monotonic()-(started if a.intro else recording_started)>20:
                    finish_recording(recorder); recorder=None
                if a.capture and not captured and time.monotonic()-started>a.capture_delay:
                    h.run(f'hl.dsp.focus({{workspace="{workspace}"}})')
                    time.sleep(.3)
                    subprocess.run(['grim',str(a.capture)],check=True)
                    captured=True
                try:
                    data=keys.recv(128)
                    if b'q' in data or b'\x03' in data: break
                    for seq,key in [(b'\x1b[A',0xad),(b'\x1b[B',0xaf),(b'\x1b[C',0xae),(b'\x1b[D',0xac)]:
                        data=data.replace(seq,bytes([key]))
                    for k in data:
                        key={ord('w'):0xad,ord('s'):0xaf,ord('a'):0xac,ord('d'):0xae,
                             ord('f'):0xa3,32:0xa2}.get(k,k)
                        if key not in held: engine.stdin.write(bytes([1,key]))
                        held[key]=time.monotonic()+.18
                except BlockingIOError: pass
                for key,until in list(held.items()):
                    if time.monotonic()>until:
                        engine.stdin.write(bytes([0,key])); del held[key]
                engine.stdin.flush()
                time.sleep(.02)
            if a.metrics:
                usage=process_usage(metric_pids)
                elapsed=time.monotonic()-started
                report={'compositor_pids':compositor_pids,'compositor_scope':compositor_scope,
                        'pixels':count,'grid':[a.cols,a.rows],'renderer':a.renderer,'fps':a.fps,
                        'foot_binary':a.foot_binary,'single_pixel_buffers':a.single_pixel_buffers,
                        'color_buffer_cache':a.color_buffer_cache,'cache_pixel_geometry':a.cache_pixel_geometry,
                        'no_pixel_frame_callback':a.no_pixel_frame_callback,
                        'gap':a.gap,
                        'freeze_after':a.freeze_after,'batch_pause':a.batch_pause,
                        'batch_size':a.batch_size,'spawn_delay':a.spawn_delay,
                        'placement_batch':a.placement_batch,'initial_size_rule':a.initial_size_rule,
                        'intro':a.intro,'font_monospace_check':a.font_monospace_check,'presentation_sample':a.presentation_sample,
                        'server_size':a.server_size,'paced_cleanup':a.paced_cleanup,
                        'setup_without_shell':a.setup_without_shell,
                        'startup_samples':startup_samples,
                        'geometry_mismatches':mismatched,'cell_size':[cell_w-a.gap,cell_h-a.gap],
                        'startup_seconds':round(startup_seconds,3),'playback_started_monotonic':started,
                        'sample_seconds':round(elapsed,3),'processes':usage['processes'],
                        'threads':usage['threads'],'rss_mib':round(usage['rss_mib'],2),
                        'cpu_seconds':round(usage['cpu_seconds']-initial_usage['cpu_seconds'],3)}
                report['cpu_cores']=round(report['cpu_seconds']/elapsed,3)
                report['process_breakdown']=[]
                for pid,initial in initial_by_pid.items():
                    current=process_usage([pid])
                    report['process_breakdown'].append({
                        'pid':pid,'role':metric_roles.get(pid,'terminal-child'),
                        'cpu_cores':round((current['cpu_seconds']-initial['cpu_seconds'])/elapsed,4),
                        'rss_mib':round(current['rss_mib'],2),
                        'present_at_end':bool(current['processes'])})
                report['compositor_samples']=samples
                a.metrics.parent.mkdir(parents=True,exist_ok=True)
                a.metrics.write_text(json.dumps(report,indent=2)+'\n')
                print(json.dumps(report),flush=True)
        except KeyboardInterrupt:
            pass
        except Exception as exc:
            if a.metrics:
                a.metrics.write_text(json.dumps({'status':'failed','error':str(exc),
                    'error_type':type(exc).__name__,'opened':opened,'requested':count,
                    'startup_samples':startup_samples},indent=2)+'\n')
            raise
        finally:
            if intro: intro.close()
            if recorder: finish_recording(recorder)
            # Avoid a second event storm from destroying the entire mosaic.
            # Keep an active lock client intact if the user locked the session.
            if a.setup_without_shell and not shell_stopped:
                if subprocess.run(['omarchy-hyprland-session-locked']).returncode==1:
                    shell_stopped=True
                    try:
                        subprocess.run(['quickshell','kill','-p','/usr/share/omarchy/shell'],
                                       timeout=10,stdout=log,stderr=log)
                    except subprocess.TimeoutExpired:
                        print('Shell shutdown timed out; continuing demo cleanup',file=sys.stderr)
            try:
                # Switch away before mass destruction so the compositor needn't
                # repaint thousands of disappearing surfaces on the visible workspace.
                if cleanup_request(lambda: h.request('activeworkspace',True))['id']==workspace:
                    cleanup_request(lambda: h.run(f'hl.dsp.focus({{workspace={json.dumps(previous)}}})'))
                    if previous_window and any(w['address']==previous_window for w in h.request('clients',True)):
                        cleanup_request(lambda: h.focus(previous_window))
                if installed:
                    cleanup_request(lambda: h.request(
                        f'eval if {rule} then {rule}:set_enabled(false); {rule}=nil end'))
            finally:
                cleanup_started=time.monotonic(); cleanup_groups=[]
                server_pids={server.pid for server in servers}
                # Stop engine and PTY writers before closing terminal servers.
                ordered=([proc for proc in reversed(procs) if proc.pid not in server_pids]
                         +list(reversed(servers))) if a.paced_cleanup else list(reversed(procs))
                for proc in ordered:
                    if proc.poll() is None:
                        proc.send_signal(signal.SIGCONT)
                        proc.terminate()
                        try: proc.wait(timeout=4)
                        except subprocess.TimeoutExpired: proc.kill(); proc.wait()
                    if a.paced_cleanup and proc.pid in server_pids:
                        group_started=time.monotonic(); settled=False; last_error=None
                        # Bound the recovery wait; cleanup must still terminate all servers.
                        while time.monotonic()-group_started<15:
                            ping=time.monotonic()
                            try:
                                remaining=h.request('clients',True)
                                latency=(time.monotonic()-ping)*1000
                                if not any(w['pid']==proc.pid and w['class']==app for w in remaining) and latency<250:
                                    settled=True; break
                            except (TimeoutError,OSError) as exc: last_error=str(exc)
                            time.sleep(.25)
                        cleanup_groups.append({'pid':proc.pid,'settled':settled,
                            'seconds':round(time.monotonic()-group_started,3),'last_error':last_error})
                        time.sleep(.1)
                if a.metrics:
                    a.metrics.with_suffix('.cleanup.json').write_text(json.dumps({
                        'paced':a.paced_cleanup,'seconds':round(time.monotonic()-cleanup_started,3),
                        'server_groups':cleanup_groups},indent=2)+'\n')
                keys.close(); log.close()
                if a.metrics:
                    a.metrics.with_suffix('.foot.log').write_text((tmp/'foot.log').read_text())
                if shell_stopped:
                    wait_for_desktop(h,app)
                    subprocess.run(['omarchy','restart','shell'],check=True,timeout=30)


def read_comm(path):
    try: return (path/'comm').read_text().strip()
    except (FileNotFoundError,PermissionError,ProcessLookupError): return ''


def wait_for_desktop(h,app,timeout=90):
    """Let window destruction finish before a fresh shell queries all windows."""
    deadline=time.monotonic()+timeout; stable=0
    while time.monotonic()<deadline:
        started=time.monotonic()
        try:
            clients=h.request('clients',True)
            ready=not any(w['class']==app for w in clients)
            ready=ready and time.monotonic()-started<.1
        except TimeoutError:
            ready=False
        stable=stable+1 if ready else 0
        if stable>=3: return True
        time.sleep(1)
    print('Desktop still busy after cleanup; attempting shell restore anyway',file=sys.stderr)
    return False


def cleanup_request(operation):
    # Destroying thousands of windows can temporarily stall compositor IPC.
    for attempt in range(5):
        try:
            return operation()
        except TimeoutError:
            if attempt == 4: raise
            time.sleep(1)


def process_usage(pids):
    usage={'cpu_seconds':0.0,'rss_mib':0.0,'threads':0,'processes':0}
    ticks=os.sysconf('SC_CLK_TCK'); page=os.sysconf('SC_PAGE_SIZE')
    for pid in set(pids):
        try:
            fields=Path(f'/proc/{pid}/stat').read_text().rsplit(')',1)[1].split()
            usage['cpu_seconds']+=(int(fields[11])+int(fields[12]))/ticks
            usage['rss_mib']+=int(fields[21])*page/1048576
            usage['threads']+=int(fields[17]); usage['processes']+=1
        except (FileNotFoundError,ProcessLookupError): pass
    return usage


def finish_recording(proc):
    if proc.poll() is None:
        proc.send_signal(signal.SIGINT)
        try: proc.wait(timeout=10)
        except subprocess.TimeoutExpired: proc.kill(); proc.wait()
    if proc.returncode:
        print('Recording failed; the live terminal preview is still available.',file=sys.stderr)


def place(h, app, placed, cols, cell_w, cell_h, x0, y0,gap=2,placement_batch=16):
    pending=[]; resized=0; resized_from=set(); started=time.monotonic()
    for w in h.request('clients',True):
        if w['class']!=app or w['address'] in placed or w['title'].endswith('-backdrop'): continue
        i=int(w['title'].rsplit('-',1)[1]); selector=json.dumps('address:'+w['address'])
        actions=[]
        # Foot normally opens at the requested pixel size already. A redundant
        # resize still triggers compositor work and desktop window events.
        if w['size']!=[cell_w-gap,cell_h-gap]:
            actions.append(f'hl.dsp.window.resize({{window={selector},x={cell_w-gap},y={cell_h-gap}}})')
            resized+=1
            resized_from.add(tuple(w['size']))
        actions.append(f'hl.dsp.window.move({{window={selector},x={x0+(i%cols)*cell_w},y={y0+(i//cols)*cell_h}}})')
        pending.append((w['address'],actions))
    for start in range(0,len(pending),placement_batch):
        batch=pending[start:start+placement_batch]
        h.run(*(action for _,actions in batch for action in actions))
        placed.update(address for address,_ in batch)
    return {'placement_ms':round((time.monotonic()-started)*1000,2),
            'placed':len(pending),'resized':resized,'resized_from':sorted(resized_from)}


if __name__=='__main__':
    main()

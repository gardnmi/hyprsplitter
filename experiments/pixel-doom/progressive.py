#!/usr/bin/env python3
"""Continuous live DOOM; add real terminals by splitting coarse image cells."""
import argparse
import json
import os
import re
import statistics
from pathlib import Path
import signal
import socket
import struct
import sys
import subprocess
import tempfile
import time

from run import build, Hyprland, open_window, finish_recording, process_usage
from benchmark_lifecycle import wait_for, stop, cpu_seconds, request as bounded_request
from regions import split_region, fixed_regions
from window_events import WindowEvents


class CaptureHidden(RuntimeError):
    pass


class StressHyprland(Hyprland):
    """Use the existing 15-second experiment IPC timeout, only in private sessions."""
    def __init__(self):
        super().__init__()
        pid=int((Path(self.path).parent/'hyprland.lock').read_text().splitlines()[0])
        if (os.environ.get('PIXEL_DOOM_DISPOSABLE_SESSION')!='1' or
            Path(f'/proc/{pid}/exe').resolve()!=Path('/tmp/pixel-doom-hyprland-build/Hyprland')):
            raise RuntimeError('Long IPC waits require the private disposable compositor')

    def request(self, command, parse=False):
        result=bounded_request(self.path,('j/' if parse else '/')+command)
        if parse:return json.loads(result)
        if result.strip()!='ok':raise RuntimeError(f'Hyprland rejected {command}: {result}')
        return result


def checkpoint_screenshot(path, timeout=10):
    """A diagnostic image must not terminate otherwise valid playback."""
    try:
        subprocess.run(['grim',str(path)],check=True,timeout=timeout)
    except (subprocess.TimeoutExpired,subprocess.CalledProcessError,OSError) as error:
        path.unlink(missing_ok=True)
        print(f'WARNING: checkpoint screenshot skipped: {error}',flush=True)
        return dict(status='failed',error_type=type(error).__name__,error=str(error))
    return dict(status='saved',path=path.name)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--levels',type=int,default=3,help='Successive four-way refinements starting at 40 terminals')
    p.add_argument('--max-terminals',type=int,help='Stop at a bounded partial refinement')
    p.add_argument('--timeout',type=float,default=180,help='Maximum progression runtime before cleanup')
    p.add_argument('--allow-slow',action='store_true',help='Keep growing through slow responses; allow up to 15s per private IPC read')
    p.add_argument('--combined-geometry',action='store_true')
    p.add_argument('--prestart-record',action='store_true')
    p.add_argument('--static-grid',action='store_true',help='Build final black grid before starting DOOM')
    p.add_argument('--split-batch',type=int,default=8,help='Parents refined per compositor query')
    p.add_argument('--hold',type=float,default=3,help='Seconds to show each completed resolution')
    p.add_argument('--fps',type=int,default=35)
    p.add_argument('--foot-binary',default='/tmp/pixel-doom-foot-build/foot')
    p.add_argument('--source',type=Path,default=Path.home()/'Projects/terminal-doom')
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--record',type=Path)
    a=p.parse_args()
    if not 1<=a.levels<=7 or not 1<=a.hold<=15 or not 1<=a.fps<=35:
        p.error('Use 1–7 levels, 1–15 second holds and 1–35 FPS')
    if not 30<=a.timeout<=7200:p.error('Timeout must be 30–7200 seconds')
    if a.allow_slow and os.environ.get('PIXEL_DOOM_DISPOSABLE_SESSION')!='1':
        p.error('--allow-slow requires a disposable nested session')
    maximum=min(64000,40*4**(a.levels-1))
    if a.max_terminals is not None:
        if not 40<=a.max_terminals<=maximum:p.error('Terminal cap must be 40 through the level maximum')
        maximum=a.max_terminals
    if not 1<=a.split_batch<=16:p.error('Split batch must be 1–16')
    if maximum+2>int(Path('/proc/sys/kernel/pty/max').read_text())-int(Path('/proc/sys/kernel/pty/nr').read_text()):
        p.error('Insufficient available PTYs')
    if int(next(x.split()[1] for x in Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')))<8*1024*1024:
        p.error('Keep at least 8 GiB memory available')
    a.output=a.output.resolve();a.output.mkdir(parents=True,exist_ok=True)
    engine_bin=Path('/tmp/hyprsplitter-pixel-doom-bridge');build(a.source,engine_bin)
    hub_bin=Path('/tmp/pixel-doom-hub')
    subprocess.run(['gcc','-std=gnu11','-O2','-Wall','-Wextra',str(Path(__file__).with_name('hub.c')),'-o',str(hub_bin)],check=True)
    h=StressHyprland() if a.allow_slow else Hyprland(); compositor_pid=int((Path(h.path).parent/'hyprland.lock').read_text().splitlines()[0]); previous=h.request('activeworkspace',True)['name']
    monitor=next(m for m in h.request('monitors',True) if m['focused'])
    width,height=int(monitor['width']/monitor['scale']),int(monitor['height']/monitor['scale'])
    pixel_scale=min((width-40)//320,(height-70)//200)
    if pixel_scale<1 or (maximum>10240 and pixel_scale<3):
        p.error('Fine-grid runs need a larger host: use --host-size 1280x800 with preview_progressive.py')
    gw,gh=320*pixel_scale,200*pixel_scale
    ox,oy=monitor['x']+(width-gw)//2,monitor['y']+(height-gh)//2
    used={w['id'] for w in h.request('workspaces',True)}
    workspace=next(i for i in range(90,10000) if i not in used)
    app=f'pixel-doom-progressive-{os.getpid()}';rule=f'progressive_{os.getpid()}'
    servers=[];hubs=[];engine=recorder=hud=None;installed=False;stages=[];windows={};rectangles={};sequence={}
    began=time.monotonic()
    def interrupted(*_):raise KeyboardInterrupt
    signal.signal(signal.SIGTERM,interrupted);signal.signal(signal.SIGINT,interrupted)
    with tempfile.TemporaryDirectory(prefix='pdgrow-') as directory, (a.output/'foot.log').open('w') as log:
        tmp=Path(directory);frame=tmp/'frame.rgb';frame.write_bytes(bytes(320*200*3))
        regions=tmp/'regions';regions.write_bytes(bytes(maximum*16));rfd=os.open(regions,os.O_RDWR)
        keys=socket.socket(socket.AF_UNIX,socket.SOCK_DGRAM);keys.bind(str(tmp/'keys'));keys.setblocking(False)
        events=WindowEvents(Path(h.path).with_name('.socket2.sock'),app)
        status=tmp/'count';status.write_text('40')
        def update_count():
            pending=tmp/'count-next';pending.write_text(str(len(rectangles)));pending.replace(status)
        def region(index,box):
            seq=sequence.get(index,0)+2;sequence[index]=seq
            os.pwrite(rfd,struct.pack('<I',seq-1),index*16)
            os.pwrite(rfd,struct.pack('<4H',*box),index*16+4)
            os.pwrite(rfd,struct.pack('<I',seq),index*16)
            rectangles[index]=box
        def geometry(box):
            x0,y0,x1,y1=box
            left=ox+x0*gw//320;top=oy+y0*gh//200
            return left,top,ox+x1*gw//320-left,oy+y1*gh//200-top
        def server_for(index):
            group=max(0,index)//128
            while len(servers)<=group:
                g=len(servers);sock=tmp/f'f{g}';hs=tmp/f'h{g}'
                env=os.environ|{'FOOT_PIXEL_DOOM':'1'}
                for name in ('FOOT_PIXEL_DOOM_CACHE','FOOT_PIXEL_DOOM_NO_CALLBACK','FOOT_PIXEL_DOOM_CACHE_GEOMETRY','FOOT_PIXEL_DOOM_SAMPLE_TITLE'):
                    env.pop(name,None)
                if g==0:env['FOOT_PIXEL_DOOM_SAMPLE_TITLE']=app+'-19'
                server=subprocess.Popen([a.foot_binary,*(['--presentation-timings'] if g==0 else []),'--config=/dev/null',f'--server={sock}',
                    '-o','font=monospace:pixelsize=1','-o','pad=0x0','-o','resize-by-cells=no','-o','workers=0',
                    '-o','scrollback.lines=0','-o','tweak.font-monospace-warn=no'],env=env,stdout=log,stderr=log)
                servers.append(server);wait_for(sock.exists)
                hub=subprocess.Popen([str(hub_bin),str(frame),str(hs),str(tmp/'keys'),'129',str(a.fps),str(regions)],stdout=log,stderr=log)
                hubs.append(hub);wait_for(hs.exists)
            return tmp/f'f{group}',tmp/f'h{group}'
        def create(index,box):
            if index>=0:region(index,box)
            sock,hs=server_for(index);_,_,w,hh=geometry(box)
            open_window(sock,app,f'{app}-{index}',w,hh,[str(hub_bin),'attach',str(hs),str(index)],True)
        def discover(indices):
            windows.update(events.discover(indices))
        def placement_actions(index,box):
            x,y,w,hh=geometry(box);selector=json.dumps('address:'+windows[index])
            if a.combined_geometry:
                return [f'hl.dsp.window.pixel_geometry({{window={selector},x={x},y={y},width={w},height={hh}}})']
            return [f'hl.dsp.window.resize({{window={selector},x={w},y={hh}}})',
                    f'hl.dsp.window.move({{window={selector},x={x},y={y}}})']
        def place(index,box):h.run(*placement_actions(index,box))
        def grid_clients():
            # Full j/clients computes unrelated metadata (including repeated
            # focus-history scans). Read only geometry via lazy Lua objects.
            prefix=app+'-'
            code=(f'local rows={{}}; for _,w in ipairs(hl.get_windows({{class={json.dumps(app)}}})) do '
                  f'local i=tonumber(w.title:sub({len(prefix)+1})); if i and i>=0 then '
                  'local p=w.at; local s=w.size; rows[#rows+1]=string.format("%d,%d,%d,%d,%d",i,p.x,p.y,s.x,s.y) '
                  'end end; return table.concat(rows,"\\n")')
            raw=bounded_request(h.path,'repl '+code)
            result=[]
            for line in raw.strip().splitlines():
                i,x,y,w,hh=map(int,line.split(','))
                result.append(dict(title=prefix+str(i),at=[x,y],size=[w,hh]))
            return result
        def capture_workspace_visible():
            expected=os.environ.get('PIXEL_DOOM_CAPTURE_WORKSPACE')
            if not expected:return True
            current=json.loads(bounded_request(os.environ['PIXEL_DOOM_PARENT_IPC'],'j/activeworkspace'))
            return current['id']==int(expected)
        def wait_visible():
            print('CAPTURE PAUSED: grid preserved; return to workspace 5 to resume',flush=True)
            while not capture_workspace_visible():time.sleep(.25)
            time.sleep(1)
        def validate_grid(level):
            clients=grid_clients()
            if len(clients)!=len(rectangles):raise RuntimeError('Unexpected terminal count')
            coverage=set();area=0
            for x0,y0,x1,y1 in rectangles.values():
                area+=(x1-x0)*(y1-y0)
                for y in range(y0,y1):coverage.update(range(y*320+x0,y*320+x1))
            if area!=64000 or len(coverage)!=64000:raise RuntimeError('Source image has holes or overlapping regions')
            mismatches=[]
            for w in clients:
                index=int(w['title'].removeprefix(app+'-'));x,y,cw,ch=geometry(rectangles[index])
                if w['size']!=[cw,ch] or w['at']!=[x,y]:
                    mismatches.append(dict(index=index,expected_size=[cw,ch],actual_size=w['size'],
                                           expected_position=[x,y],actual_position=w['at']))
            if mismatches:
                (a.output/'geometry-mismatches.json').write_text(json.dumps(dict(
                    level=level,terminals=len(clients),initial_monitor=monitor,
                    mosaic=dict(width=gw,height=gh,x=ox,y=oy),mismatches=mismatches),indent=2)+'\n')
                raise RuntimeError(f'Incorrect terminal geometry: {[m["index"] for m in mismatches[:8]]}')
            return len(clients)
        def hold(level):
            started=time.monotonic();before=frame.read_bytes();cpu_before=cpu_seconds(compositor_pid)
            last_visibility_check=0
            while time.monotonic()-started<a.hold:
                if engine.poll() is not None:raise RuntimeError('DOOM stopped during progression')
                if recorder and recorder.poll() is not None:raise RuntimeError('Recorder stopped; see foot.log')
                if time.monotonic()-last_visibility_check>.25:
                    last_visibility_check=time.monotonic()
                    if not capture_workspace_visible():
                        if recorder:
                            finish_recording(recorder)
                            a.record.unlink(missing_ok=True)
                        raise CaptureHidden('Capture workspace hidden; discard this playback sample')
                try:
                    if b'q' in keys.recv(128).lower():raise KeyboardInterrupt
                except BlockingIOError:pass
                time.sleep(.05)
            if frame.read_bytes()==before:raise RuntimeError('DOOM frame stopped changing')
            core_usage=(cpu_seconds(compositor_pid)-cpu_before)/(time.monotonic()-started)
            count=static_validated_count if a.static_grid else validate_grid(level)
            feedback=[int(latency)/1000 for stamp,latency in re.findall(r'PD_PRESENT time_ns=(\d+) latency_us=(\d+)',(a.output/'foot.log').read_text()) if int(stamp)/1e9>=started]
            usage=process_usage([compositor_pid,engine.pid,*[s.pid for s in servers],*[h.pid for h in hubs]])
            stages.append(dict(compositor_cores=round(core_usage,3),rss_mib=round(usage['rss_mib'],1),
                sampled_presentations=len(feedback),presentation_latency_median_ms=statistics.median(feedback) if feedback else None,level=level,terminals=count,engine_pid=engine.pid,
                               seconds=round(time.monotonic()-playback_started,3),geometry_mismatches=0))
            (a.output/'progression.json').write_text(json.dumps(dict(status='running',stages=stages,engine_pid=engine.pid,continuous_engine=True,identity_intro=False),indent=2)+'\n')
            stages[-1]['screenshot']=(dict(status='skipped',reason='static playback sample') if a.static_grid else checkpoint_screenshot(a.output/f'level-{level}-{count}.png'))
            (a.output/'progression.json').write_text(json.dumps(dict(status='running',stages=stages,engine_pid=engine.pid,continuous_engine=True,identity_intro=False),indent=2)+'\n')
            print(json.dumps(stages[-1]),flush=True)
        try:
            # Place new windows outside the mosaic until their live color is ready.
            h.request(f'eval {rule}=hl.window_rule({{name="{rule}",match={{class="^{app}$"}},workspace="{workspace} silent",float=true,no_anim=true,no_initial_focus=true,border_size=0,rounding=0,no_shadow=true,no_blur=true,opacity="1 override 1 override",move={{{monitor["x"]+width+100},{monitor["y"]}}}}})')
            installed=True
            h.run(f'hl.dsp.focus({{workspace="{workspace}"}})')
            create(-1,(0,0,320,200));discover([-1])
            # Exercise the finest native-pixel size before opening the mosaic.
            # Foot's minimum cell height can exceed the requested font pixelsize.
            h.run(f'hl.dsp.window.resize({{window="address:{windows[-1]}",x={pixel_scale},y={pixel_scale}}})',
                  f'hl.dsp.window.move({{window="address:{windows[-1]}",x={ox},y={oy}}})')
            if pixel_scale>=3:
                wait_for(lambda:next((w for w in h.request('clients',True) if w['address']==windows[-1]),{}).get('size')==[pixel_scale,pixel_scale],seconds=3)
            (a.output/'preflight.json').write_text(json.dumps(dict(monitor=monitor,pixel_scale=pixel_scale,
                mosaic=[gw,gh],combined_geometry=a.combined_geometry,minimum_size_checked=pixel_scale>=3),indent=2)+'\n')
            h.run(f'hl.dsp.window.resize({{window="address:{windows[-1]}",x={width},y={height}}})',
                  f'hl.dsp.window.move({{window="address:{windows[-1]}",x={monitor["x"]},y={monitor["y"]}}})')
            boxes=fixed_regions(maximum if a.static_grid else 40)
            creation_started=time.monotonic();creation_cpu=cpu_seconds(compositor_pid)
            for offset in range(0,len(boxes),32):
                if time.monotonic()-began>a.timeout:raise RuntimeError('Grid creation reached its runtime bound')
                available=int(next(x.split()[1] for x in Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')))
                if available<8*1024*1024:raise RuntimeError('Memory reserve reached')
                indices=range(offset,min(offset+32,len(boxes)))
                for i in indices:create(i,boxes[i])
                discover(indices)
                actions=[]
                for i in indices:actions.extend(placement_actions(i,boxes[i]))
                h.run(*actions);update_count()
                if len(rectangles)%512==0 or len(rectangles)==len(boxes):
                    print(f'GRID BUILD: {len(rectangles)}/{len(boxes)} terminals; DOOM not started',flush=True)
            (a.output/'creation.json').write_text(json.dumps(dict(terminals=len(boxes),static_grid=a.static_grid,
                seconds=time.monotonic()-creation_started,compositor_cpu_seconds=cpu_seconds(compositor_pid)-creation_cpu),indent=2)+'\n')
            hud=subprocess.Popen([a.foot_binary,'--config=/dev/null','-a',app,'-T',app+'--2',
                '-o','font=monospace:size=12','-o','pad=0x0','-o','resize-by-cells=no',
                '-o','tweak.font-monospace-warn=no','-o','colors-dark.background=000000',
                sys.executable,str(Path(__file__).resolve()),'hud',str(status)],stdout=log,stderr=log)
            discover([-2])
            h.run(f'hl.dsp.window.resize({{window="address:{windows[-2]}",x=400,y=26}})',
                  f'hl.dsp.window.move({{window="address:{windows[-2]}",x={ox},y={max(monitor["y"]+5,oy-32)}}})')
            static_validated_count=None
            if a.static_grid:
                checked=time.monotonic();static_validated_count=validate_grid(-2)
                (a.output/'geometry.json').write_text(json.dumps(dict(terminals=static_validated_count,
                    mismatches=0,seconds=time.monotonic()-checked,phase='before playback'),indent=2)+'\n')
            if os.environ.get('PIXEL_DOOM_CAPTURE_WORKSPACE'):
                print('GRID READY: waiting for capture workspace to be visible',flush=True)
                if os.environ.get('PIXEL_DOOM_FOCUS_CAPTURE')=='1':
                    target=os.environ['PIXEL_DOOM_CAPTURE_WORKSPACE']
                    bounded_request(os.environ['PIXEL_DOOM_PARENT_IPC'],f'eval hl.dispatch(hl.dsp.focus({{workspace="{target}"}}))')
                while not capture_workspace_visible():time.sleep(.25)
                time.sleep(1)
            def start_recording():
                nonlocal recorder
                a.record.parent.mkdir(parents=True,exist_ok=True)
                capture_env=os.environ.copy();capture_args=['-o',monitor['name']]
                if os.environ.get('PIXEL_DOOM_CAPTURE_DISPLAY'):
                    capture_env.update(WAYLAND_DISPLAY=os.environ['PIXEL_DOOM_CAPTURE_DISPLAY'],XDG_RUNTIME_DIR=os.environ['PIXEL_DOOM_CAPTURE_RUNTIME'])
                    capture_args=['-g',os.environ['PIXEL_DOOM_CAPTURE_GEOMETRY']]
                recorder=subprocess.Popen(['/tmp/pixel-doom-wf-recorder-build/wf-recorder',*capture_args,
                    '-c','libx264','-p','preset=ultrafast','-p','crf=18','-p','threads=2','-x','yuv420p',
                    '-r','35','-F','pad=ceil(iw/2)*2:ceil(ih/2)*2','--no-dmabuf','-f',str(a.record.resolve())],stdout=log,stderr=log,env=capture_env)
            if a.prestart_record:
                if not a.record or not a.static_grid:raise RuntimeError('Prestart capture requires a recorded static grid')
                capture_started=time.monotonic();start_recording()
                wait_for(lambda:a.record.exists() and a.record.stat().st_size>0,seconds=30)
                (a.output/'capture.json').write_text(json.dumps(dict(playback_offset=time.monotonic()-capture_started,
                    terminal_update_hz=a.fps,prestarted=True),indent=2)+'\n')
            with (a.output/'engine.log').open('w') as engine_log:
                engine=subprocess.Popen([str(engine_bin),str(frame),'320','200','-iwad',str(a.source/'doom1.wad'),
                    '-config',str(tmp/'doom.cfg'),'-nosound','-playdemo','demo1'],cwd=tmp,stdin=subprocess.PIPE,
                    stdout=engine_log,stderr=engine_log,env=os.environ|{'PIXEL_DOOM_OUTPUT_FPS':str(a.fps),'PIXEL_DOOM_LOOP_DEMO':'1'})
            playback_started=time.monotonic()
            if a.static_grid and a.record and not a.prestart_record:
                # Measure playback without recording, then capture the same
                # already-created terminals; avoid rebuilding a large grid.
                while True:
                    try:hold(-1);break
                    except CaptureHidden:wait_visible()
            if a.record and not a.prestart_record:start_recording()
            while True:
                try:hold(0);break
                except CaptureHidden:
                    if not a.static_grid:raise
                    wait_visible()
                    if a.record:start_recording()
            for level in range(1,1 if a.static_grid else a.levels):
                parents=list(rectangles.items())
                # Refine each coarse cell in place. The existing terminal stays;
                # three new terminal windows complete its four live quadrants.
                for offset in range(0,len(parents),a.split_batch):
                    if engine.poll() is not None:raise RuntimeError('DOOM stopped during creation')
                    if len(rectangles)>=maximum:break
                    if time.monotonic()-began>a.timeout:raise RuntimeError('Progression reached its runtime bound')
                    available=int(next(x.split()[1] for x in Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')))
                    if available<8*1024*1024:raise RuntimeError('Memory reserve reached')
                    pending=[];new_indices=[]
                    for index,(x0,y0,x1,y1) in parents[offset:offset+a.split_batch]:
                        remaining=maximum-len(rectangles)
                        if remaining<=0:break
                        boxes=split_region((x0,y0,x1,y1),remaining)
                        if len(boxes)==1:continue
                        first=len(rectangles);indices=list(range(first,first+len(boxes)-1))
                        for child,box in zip(indices,boxes[1:]):create(child,box)
                        new_indices.extend(indices);pending.append((index,boxes,indices))
                    if not pending:continue
                    discover(new_indices)
                    actions=[]
                    for index,boxes,indices in pending:
                        for child,box in zip(indices,boxes[1:]):actions.extend(placement_actions(child,box))
                        region(index,boxes[0]);actions.extend(placement_actions(index,boxes[0]))
                    ping=time.monotonic();h.run(*actions)
                    response_seconds=time.monotonic()-ping
                    if response_seconds>.5:
                        if not a.allow_slow:raise RuntimeError('Compositor response exceeded 500ms')
                        print(f'SLOW RESPONSE: {response_seconds:.3f}s at {len(rectangles)} terminals; continuing',flush=True)
                    update_count()
                    if (len(rectangles)//512)!=((len(rectangles)-len(new_indices))//512):
                        print(f'LIVE GROWTH: {len(rectangles)} terminal pixels; DOOM PID {engine.pid}',flush=True)
                hold(level)
                if len(rectangles)>=maximum:break
            (a.output/'progression.json').write_text(json.dumps(dict(status='complete',stages=stages,
                engine_pid=engine.pid,continuous_engine=True,identity_intro=False),indent=2)+'\n')
        except BaseException as error:
            (a.output/'progression.json').write_text(json.dumps(dict(status='failed',error=str(error),
                error_type=type(error).__name__,allocated_regions=len(rectangles),stages=stages,
                engine_pid=engine.pid if engine else None,continuous_engine=True,identity_intro=False),indent=2)+'\n')
            raise
        finally:
            if recorder:finish_recording(recorder)
            stop(engine)
            if os.environ.get('PIXEL_DOOM_DISPOSABLE_SESSION')=='1':
                # Capture is finalized. Drop the disposable compositor before
                # closing thousands of PTYs, rather than processing each unmap.
                (a.output/'close-nested').touch()
                for proc in [hud,*hubs,*servers]:
                    if proc is not None and proc.poll() is None:proc.terminate()
            stop(hud)
            for hub in reversed(hubs):stop(hub)
            if os.environ.get('PIXEL_DOOM_DISPOSABLE_SESSION')=='1':
                # The wrapper owns this compositor and can discard the whole
                # session after the recording has finalized. Avoid O(N²) unmaps.
                for server in servers:
                    if server.poll() is None:server.terminate()
                (a.output/'close-nested').touch()
                for server in servers:stop(server)
                os.close(rfd);keys.close();events.close()
            else:
                try:
                    if h.request('activeworkspace',True)['id']==workspace:
                        h.run(f'hl.dsp.focus({{workspace={json.dumps(previous)}}})')
                    if installed:h.request(f'eval if {rule} then {rule}:set_enabled(false); {rule}=nil end')
                finally:
                    for server in reversed(servers):stop(server);time.sleep(.1)
                    os.close(rfd);keys.close();events.close()
                wait_for(lambda:not [w for w in h.request('clients',True) if w['class']==app])



def hud_count(path):
    previous=None
    print('\033[?25l',end='',flush=True)
    while True:
        value=path.read_text()
        if value!=previous:
            print(f'\033[H\033[2K{int(value):,} terminal pixels',end='',flush=True)
            previous=value
        time.sleep(.05)


if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1]=='hud':hud_count(Path(sys.argv[2]))
    else:main()

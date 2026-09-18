"""Bounded synthetic OSC11 comparison; isolated terminal instances, no user config."""
import argparse,json,os,signal,subprocess,sys,tempfile,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from hyprsplitter import Hyprland
from foot_ipc import open_window
from run import process_usage,read_comm

p=argparse.ArgumentParser();p.add_argument('terminal',choices=['foot','ghostty']);p.add_argument('--count',type=int,default=64);p.add_argument('--seconds',type=int,default=10);a=p.parse_args()
assert 1<=a.count<=64 and 1<=a.seconds<=20
out=Path(__file__).with_name('output');out.mkdir(exist_ok=True)
source=out/'color-load.c';binary=out/'color-load'
source.write_text(r'''#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <time.h>
#include <unistd.h>
int main(void) {
  write(1,"\033[?25l\033[2J",10);
  for(int i=0;i<1800;i++) {
    struct timespec t; clock_gettime(CLOCK_MONOTONIC,&t);
    unsigned frame=(unsigned)(t.tv_sec*15+t.tv_nsec/66666667);
    char b[32]; int n=snprintf(b,sizeof b,"\033]11;#%06x\a",(frame*7919u)&0xffffff);
    if(write(1,b,n)!=n) return 0;
    struct timespec delay={0,66666667}; nanosleep(&delay,0);
  }
}
''')
subprocess.run(['gcc','-O2',str(source),'-o',str(binary)],check=True)
h=Hyprland();previous=h.request('activeworkspace',True)['name'];occupied={w['id'] for w in h.request('workspaces',True)};workspace=next(i for i in range(90,1000) if i not in occupied)
app=f'org.hyprsplitter.Compare{os.getpid()}';rule=f'compare_{os.getpid()}'
comp=[int(p.name) for p in Path('/proc').iterdir() if p.name.isdigit() and read_comm(p)=='Hyprland']
proc=None;helper_pids=[];report={'terminal':a.terminal,'count':a.count,'fps':15,'phases':{},'app':app};started=time.monotonic()
def stop(*_): raise KeyboardInterrupt
signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
with tempfile.TemporaryDirectory(prefix='terminal-compare-') as tmp, (out/f'compare-{a.terminal}-{a.count}.log').open('w') as log:
 try:
  h.request(f'eval {rule}=hl.window_rule({{name="{rule}",match={{class="^{app}$"}},workspace="{workspace} silent",float=true,no_anim=true,no_initial_focus=true,border_size=0,rounding=0,no_shadow=true,no_blur=true,opacity="1 override 1 override",size={{150,90}}}})')
  env=os.environ.copy();env.pop('FOOT_PIXEL_DOOM_CACHE',None);env.pop('FOOT_PIXEL_DOOM_NO_CALLBACK',None)
  if a.terminal=='foot':
   env['FOOT_PIXEL_DOOM']='1';sock=Path(tmp)/'foot.sock'
   proc=subprocess.Popen(['/tmp/pixel-doom-foot-build/foot','--config=/dev/null',f'--server={sock}','-o','workers=0','-o','scrollback.lines=0','-o','font=monospace:size=2','-o','pad=0x0','-o','resize-by-cells=no'],env=env,stdout=log,stderr=log)
   deadline=time.monotonic()+10
   while not sock.exists():
    if proc.poll() is not None or time.monotonic()>deadline: raise RuntimeError('Foot server failed')
    time.sleep(.05)
  else:
   cmd=['ghostty','--config-default-files=false',f'--class={app}','--gtk-single-instance=true','--linux-cgroup=never',f'--command={binary.resolve()}','--shell-integration=none','--confirm-close-surface=false','--window-decoration=none','--font-size=2','--window-padding-x=0','--window-padding-y=0','--scrollback-limit=0','--background-opacity=1','--quit-after-last-window-closed=true']
   proc=subprocess.Popen(cmd,stdout=log,stderr=log)
  for i in range(a.count):
   if a.terminal=='foot': open_window(sock,app,f'color-{i}',150,90,[binary.resolve()],False)
   elif i: subprocess.run(cmd,stdout=log,stderr=log,timeout=10,check=True)
   deadline=time.monotonic()+10
   while True:
    windows=[w for w in h.request('clients',True) if w['class']==app]
    if len(windows)>=i+1: break
    if proc.poll() is not None or time.monotonic()>deadline: raise RuntimeError(f'Window {i} failed')
    time.sleep(.05)
   usage=process_usage([proc.pid])
   if usage['rss_mib']>1500 or usage['threads']>512: raise RuntimeError('Resource guard stopped creation')
   time.sleep(.03)
  report['startup_seconds']=round(time.monotonic()-started,3)
  report['window_pids']=sorted({w['pid'] for w in windows})
  if report['window_pids']!=[proc.pid]: raise RuntimeError('Windows did not share one process')
  for i,w in enumerate(windows):
   sel=json.dumps('address:'+w['address'])
   h.run(f'hl.dsp.window.resize({{window={sel},x=150,y=90}})',f'hl.dsp.window.move({{window={sel},x={200+(i%8)*152},y={100+(i//8)*92}}})')
  windows=[w for w in h.request('clients',True) if w['class']==app]
  report['sizes']=sorted({tuple(w['size']) for w in windows})
  h.run(f'hl.dsp.focus({{workspace="{workspace}"}})')
  time.sleep(2)
  helper_pids=[]
  for task in Path('/proc').iterdir():
   if not task.name.isdigit(): continue
   try:
    if (task/'exe').resolve()==binary.resolve():helper_pids.append(int(task.name))
   except (FileNotFoundError,PermissionError,ProcessLookupError):pass
  if len(helper_pids)!=a.count: raise RuntimeError(f'Expected {a.count} helper processes, found {len(helper_pids)}')
  for phase in ['visible','hidden']:
   target=str(workspace) if phase=='visible' else previous
   # Stop if the user switched away during the preceding visible phase.
   h.run(f'hl.dsp.focus({{workspace={json.dumps(target)}}})')
   time.sleep(2)
   samples=[];before=process_usage([proc.pid]);helpers_before=process_usage(helper_pids);last_comp=process_usage(comp)['cpu_seconds'];t0=last=time.monotonic()
   for _ in range(a.seconds):
    time.sleep(1);now=time.monotonic();ping=time.monotonic();active=h.request('activeworkspace',True)['id'];latency=(time.monotonic()-ping)*1000;cpu=process_usage(comp)['cpu_seconds'];u=process_usage([proc.pid]);samples.append({'visible':active==workspace,'hyprland_cores':round((cpu-last_comp)/(now-last),4),'ipc_ms':round(latency,2)})
    last_comp=cpu;last=now
    if (phase=='visible' and active!=workspace) or latency>250 or not u['processes']: raise RuntimeError('Visibility/responsiveness changed; stop comparison')
   elapsed=time.monotonic()-t0;after=process_usage([proc.pid]);helpers_after=process_usage(helper_pids)
   report['phases'][phase]={'terminal_cores':round((after['cpu_seconds']-before['cpu_seconds'])/elapsed,4),'rss_mib':round(after['rss_mib'],2),'threads':after['threads'],'helper_cores':round((helpers_after['cpu_seconds']-helpers_before['cpu_seconds'])/elapsed,4),'helper_count':helpers_after['processes'],'samples':samples}
   print(phase,json.dumps(report['phases'][phase]),flush=True)
  report['status']='complete'
 except BaseException as e:
  report['status']='stopped';report['error']=str(e);raise
 finally:
  if proc and proc.poll() is None:
   proc.terminate()
   try:proc.wait(timeout=8)
   except subprocess.TimeoutExpired:proc.kill();proc.wait()
  for pid in helper_pids:
   try:
    if read_comm(Path(f'/proc/{pid}'))=='color-load':os.kill(pid,signal.SIGTERM)
   except ProcessLookupError:pass
  if h.request('activeworkspace',True)['id']==workspace:h.run(f'hl.dsp.focus({{workspace={json.dumps(previous)}}})')
  h.request(f'eval if {rule} then {rule}:set_enabled(false);{rule}=nil end')
  (out/f'compare-{a.terminal}-{a.count}.json').write_text(json.dumps(report,indent=2)+'\n')

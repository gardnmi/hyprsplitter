"""Probe 1–8 pixel Foot window sizes in an isolated compositor (eight windows)."""
import sys,os,json,subprocess,tempfile,time,signal
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from benchmark_lifecycle import request,wait_for,stop
from foot_ipc import open_window
out=ROOT/'output'/'fine-geometry-probe';out.mkdir(parents=True,exist_ok=True)
comp=foot=None
with tempfile.TemporaryDirectory(prefix='pdgeom-') as d,(out/'log').open('w') as log:
 try:
  root=Path(d);rt=root/'r';rt.mkdir(mode=0o700);cfg=root/'hyprland.lua'
  cfg.write_text('''hl.monitor({output="",mode="800x600@60",position="auto",scale=1})
hl.config({animations={enabled=false},general={border_size=0,gaps_in=0,gaps_out=0},decoration={rounding=0,blur={enabled=false},shadow={enabled=false}},misc={disable_hyprland_logo=true,disable_splash_rendering=true}})
hl.window_rule({name="probe",match={class="^pixel-doom-geometry$"},float=true,no_anim=true,no_initial_focus=true,no_blur=true,no_shadow=true,border_size=0,rounding=0,opacity="1 override 1 override"})
''')
  env=os.environ.copy();parent=Path(env['WAYLAND_DISPLAY']);parent=parent if parent.is_absolute() else Path(env['XDG_RUNTIME_DIR'])/parent
  env.update(XDG_RUNTIME_DIR=str(rt),WAYLAND_DISPLAY=str(parent),HYPRLAND_NO_SD_VARS='1',HYPRLAND_PIXEL_DOOM_NESTED_ONLY='1',HYPRLAND_PIXEL_DOOM_BATCH_LIFECYCLE='1',HYPRLAND_PIXEL_DOOM_BATCH_MS='8',HYPRLAND_PIXEL_DOOM_FAST_ADDRESS='1',HYPRLAND_PIXEL_DOOM_BATCH_DRAW='1',HYPRLAND_PIXEL_DOOM_DEFER_TEXTURE='1',HYPRLAND_PIXEL_DOOM_SKIP_UNCHANGED_RULES='1')
  for k in ('HYPRLAND_INSTANCE_SIGNATURE','HYPRLAND_CMD','HYPRLAND_PIXEL_DOOM_TEXTURE_CACHE'):env.pop(k,None)
  comp=subprocess.Popen(['dbus-run-session','--','/tmp/pixel-doom-hyprland-build/Hyprland','--config',str(cfg)],env=env,stdout=log,stderr=log,start_new_session=True)
  lock=wait_for(lambda:next(rt.glob('hypr/*/hyprland.lock'),None));pid,display=lock.read_text().splitlines()[:2];ipc=lock.parent/'.socket.sock';wait_for(ipc.exists)
  sock=root/'foot';child=env|{'WAYLAND_DISPLAY':str(rt/display),'HYPRLAND_INSTANCE_SIGNATURE':lock.parent.name,'FOOT_PIXEL_DOOM':'1'}
  foot=subprocess.Popen(['/tmp/pixel-doom-foot-build/foot','--config=/dev/null',f'--server={sock}','-o','font=monospace:pixelsize=1','-o','pad=0x0','-o','resize-by-cells=no','-o','workers=0','-o','scrollback.lines=0','-o','tweak.font-monospace-warn=no'],env=child,stdout=log,stderr=log)
  wait_for(sock.exists)
  for i in range(8):open_window(sock,'pixel-doom-geometry',f'probe-{i}',24,24,[sys.executable,'-c',"import sys,time;sys.stdout.write('\033[?25l\033[2J\033]11;#ff0000\a');sys.stdout.flush();time.sleep(60)"],True)
  clients=lambda:[w for w in json.loads(request(ipc,'j/clients')) if w['class']=='pixel-doom-geometry']
  wait_for(lambda:len(clients())==8);time.sleep(.5)
  windows=clients()
  for w in windows:
   i=int(w['title'].split('-')[1]);size=i+1
   request(ipc,f'eval hl.dispatch(hl.dsp.window.resize({{window="address:{w["address"]}",x={size},y={size}}})); hl.dispatch(hl.dsp.window.move({{window="address:{w["address"]}",x={30+i*30},y=40}}))')
  time.sleep(.6)
  result=[{'requested_size':[int(w['title'].split('-')[1])+1]*2,'actual_size':w['size'],'actual_position':w['at']} for w in clients()]
  (out/'results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
 finally:
  stop(foot)
  if comp and comp.poll() is None:
   os.killpg(comp.pid,signal.SIGTERM)
   try:comp.wait(timeout=10)
   except subprocess.TimeoutExpired:os.killpg(comp.pid,signal.SIGKILL);comp.wait()

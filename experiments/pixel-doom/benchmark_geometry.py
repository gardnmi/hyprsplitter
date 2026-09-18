"""Compare separate and combined placement in an isolated compositor (512 windows)."""
import sys,os,json,subprocess,tempfile,time,signal,argparse
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from benchmark_lifecycle import request,wait_for,stop,cpu_seconds
from foot_ipc import open_window
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--fast-floating',action='store_true')
p.add_argument('--output',type=Path,required=True)
a=p.parse_args();out=a.output;out.mkdir(parents=True,exist_ok=True)
if (out/'results.json').exists():p.error('Choose a fresh results directory')
comp=foot=None
with tempfile.TemporaryDirectory(prefix='pdgeom-') as d,(out/'log').open('w') as log:
 try:
  root=Path(d);rt=root/'r';rt.mkdir(mode=0o700);cfg=root/'hyprland.lua'
  cfg.write_text('''hl.monitor({output="",mode="800x600@60",position="auto",scale=1})
hl.config({animations={enabled=false},general={border_size=0,gaps_in=0,gaps_out=0},decoration={rounding=0,blur={enabled=false},shadow={enabled=false}},misc={disable_hyprland_logo=true,disable_splash_rendering=true}})
hl.window_rule({name="probe",match={class="^pixel-doom-geometry$"},float=true,no_anim=true,no_initial_focus=true,no_blur=true,no_shadow=true,border_size=0,rounding=0,opacity="1 override 1 override"})
''')
  env=os.environ.copy();parent=Path(env['WAYLAND_DISPLAY']);parent=parent if parent.is_absolute() else Path(env['XDG_RUNTIME_DIR'])/parent
  env.update(XDG_RUNTIME_DIR=str(rt),WAYLAND_DISPLAY=str(parent),HYPRLAND_NO_SD_VARS='1',HYPRLAND_PIXEL_DOOM_NESTED_ONLY='1',HYPRLAND_PIXEL_DOOM_BATCH_LIFECYCLE='1',HYPRLAND_PIXEL_DOOM_BATCH_MS='8',HYPRLAND_PIXEL_DOOM_FAST_ADDRESS='1',HYPRLAND_PIXEL_DOOM_BATCH_DRAW='1',HYPRLAND_PIXEL_DOOM_DEFER_TEXTURE='1',HYPRLAND_PIXEL_DOOM_SKIP_UNCHANGED_RULES='1',HYPRLAND_PIXEL_DOOM_COMBINED_GEOMETRY='1')
  for k in ('HYPRLAND_INSTANCE_SIGNATURE','HYPRLAND_CMD','HYPRLAND_PIXEL_DOOM_TEXTURE_CACHE'):env.pop(k,None)
  env.pop('HYPRLAND_PIXEL_DOOM_FAST_FLOATING',None)
  if a.fast_floating:env['HYPRLAND_PIXEL_DOOM_FAST_FLOATING']='1'
  comp=subprocess.Popen(['dbus-run-session','--','/tmp/pixel-doom-hyprland-build/Hyprland','--config',str(cfg)],env=env,stdout=log,stderr=log,start_new_session=True)
  lock=wait_for(lambda:next(rt.glob('hypr/*/hyprland.lock'),None));pid,display=lock.read_text().splitlines()[:2];ipc=lock.parent/'.socket.sock';wait_for(ipc.exists)
  sock=root/'foot';child=env|{'WAYLAND_DISPLAY':str(rt/display),'HYPRLAND_INSTANCE_SIGNATURE':lock.parent.name,'FOOT_PIXEL_DOOM':'1'}
  foot=subprocess.Popen(['/tmp/pixel-doom-foot-build/foot','--config=/dev/null',f'--server={sock}','-o','font=monospace:pixelsize=1','-o','pad=0x0','-o','resize-by-cells=no','-o','workers=0','-o','scrollback.lines=0','-o','tweak.font-monospace-warn=no'],env=child,stdout=log,stderr=log)
  wait_for(sock.exists)
  def evaluate(code):
   reply=request(ipc,'eval '+code).strip()
   if reply!='ok':raise RuntimeError(reply)
  for i in range(512):
   open_window(sock,'pixel-doom-geometry',f'probe-{i}',24,24,['/usr/bin/printf','\033[?25l\033[2J\033]11;#ff0000\a'],True)
  clients=lambda:[w for w in json.loads(request(ipc,'j/clients')) if w['class']=='pixel-doom-geometry']
  wait_for(lambda:len(clients())==512);time.sleep(.5)
  windows=sorted(clients(),key=lambda w:int(w['title'].split('-')[1]))
  results=[]
  def position(combined,phase):
   size=3 if phase%2 else 6
   for offset in range(0,len(windows),32):
    actions=[]
    for i,w in enumerate(windows[offset:offset+32],offset):
     sel=json.dumps('address:'+w['address']);x=30+i%32*10+phase%2;y=40+i//32*10+phase%2
     if combined:actions.append(f'hl.dispatch(hl.dsp.window.pixel_geometry({{window={sel},x={x},y={y},width={size},height={size}}}))')
     else:
      actions.append(f'hl.dispatch(hl.dsp.window.resize({{window={sel},x={size},y={size}}}))')
      actions.append(f'hl.dispatch(hl.dsp.window.move({{window={sel},x={x},y={y}}}))')
    evaluate(';'.join(actions))
  for pair in range(3):
   for combined in ([False,True] if pair%2==0 else [True,False]):
    position(False,0);time.sleep(.2)
    start=time.monotonic();before=cpu_seconds(int(pid))
    for phase in range(1,257):position(combined,phase)
    wall=time.monotonic()-start;cpu=cpu_seconds(int(pid))-before
    expected={w['address']:[30+i%32*10,40+i//32*10] for i,w in enumerate(windows)}
    for w in clients():assert w['at']==expected[w['address']] and w['size']==[6,6],w
    result=dict(pair=pair,combined=combined,placements=131072,seconds=wall,compositor_cpu_seconds=cpu)
    results.append(result);print(json.dumps(result),flush=True)
  position(True,1);time.sleep(.3)
  for w in clients():assert w['size']==[3,3],w
  subprocess.run(['grim',str(out/'fine-grid.png')],env=child,check=True,timeout=10)
  imgwidth=int(subprocess.check_output(['magick','identify','-format','%w',str(out/'fine-grid.png')]))
  raw=subprocess.check_output(['magick',str(out/'fine-grid.png'),'-depth','8','rgb:-'])
  for i in range(512):
   x=32+i%32*10;y=42+i//32*10;actual=tuple(raw[(y*imgwidth+x)*3:(y*imgwidth+x)*3+3]);assert actual==(255,0,0),(i,actual)
  open_window(sock,'geometry-anchor','anchor',30,30,['/bin/true'],True)
  anchor=wait_for(lambda:next((w for w in json.loads(request(ipc,'j/clients')) if w['class']=='geometry-anchor'),None))
  sel=json.dumps('address:'+anchor['address'])
  reply=request(ipc,f'eval hl.dispatch(hl.dsp.window.pixel_geometry({{window={sel},x=10,y=10,width=3,height=3}}))').strip()
  assert reply!='ok','ordinary window was accepted'
  assert request(ipc,'eval hl.dispatch(hl.dsp.window.pixel_geometry({x=1,y=1,width=0,height=3}))').strip()!='ok'
  target=windows[0]['address'];sel=json.dumps('address:'+target)
  selected=lambda:next(w for w in clients() if w['address']==target)
  for mode in ('fullscreen','maximized'):
   evaluate(f'hl.dispatch(hl.dsp.window.fullscreen({{window={sel},mode="{mode}",action="set"}}))')
   wait_for(lambda:selected()['fullscreen']!=0)
   assert request(ipc,f'eval hl.dispatch(hl.dsp.window.pixel_geometry({{window={sel},x=31,y=41,width=3,height=3}}))').strip()!='ok'
   evaluate(f'hl.dispatch(hl.dsp.window.fullscreen({{window={sel},mode="{mode}",action="unset"}}))')
   wait_for(lambda:selected()['fullscreen']==0)
  evaluate(f'hl.dispatch(hl.dsp.window.float({{window={sel},action="off"}}))')
  wait_for(lambda:not selected()['floating'])
  assert request(ipc,f'eval hl.dispatch(hl.dsp.window.pixel_geometry({{window={sel},x=31,y=41,width=3,height=3}}))').strip()!='ok'
  evaluate(f'hl.dispatch(hl.dsp.window.float({{window={sel},action="on"}}))')
  wait_for(lambda:selected()['floating'])
  position(True,1)
  wait_for(lambda:selected()['at']==[31,41] and selected()['size']==[3,3])
  (out/'results.json').write_text(json.dumps(dict(trials=results,fast_floating=a.fast_floating,
      fine_grid_color_check='512 passed',ordinary_window_rejected=True,
      fullscreen_maximized_and_tiled_transitions='passed'),indent=2)+'\n')
  print('PASS: six paired placement trials, 512 tiny-window colors, and floating/fullscreen/tiled guards',flush=True)

 finally:
  stop(foot)
  if comp and comp.poll() is None:
   os.killpg(comp.pid,signal.SIGTERM)
   try:comp.wait(timeout=10)
   except subprocess.TimeoutExpired:os.killpg(comp.pid,signal.SIGKILL);comp.wait()

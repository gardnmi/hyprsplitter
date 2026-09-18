"""Check real 1x1 terminal colors, stacking, resize, and removal in a nested compositor."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
from foot_ipc import open_window
from benchmark_lifecycle import wait_for,stop
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from hyprsplitter import Hyprland

h=Hyprland()
assert os.environ.get('HYPRLAND_PIXEL_DOOM_NESTED_ONLY')=='1'
pid=int((Path(h.path).parent/'hyprland.lock').read_text().splitlines()[0])
assert str(Path(f'/proc/{pid}/exe').resolve())=='/tmp/pixel-doom-hyprland-build/Hyprland'
out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=True)
app=f'pixel-doom-batch-verify-{os.getpid()}';rule=f'batch_verify_{os.getpid()}'
colors=[(255,0,0),(0,255,0),(0,0,255),(128,64,32),(16,180,240),(220,150,10),(90,25,130),(210,210,210)]
proc=None
with tempfile.TemporaryDirectory(prefix='pdbv-') as d, (out/'verification-foot.log').open('w') as log:
 try:
  sock=Path(d)/'foot.sock'
  update=Path(d)/'update'; update.write_text('')
  h.request(f'eval {rule}=hl.window_rule({{name="{rule}",match={{class="^{app}$"}},float=true,no_anim=true,no_initial_focus=true,no_blur=true,no_shadow=true,border_size=0,rounding=0,size={{50,40}},opacity="1 override 1 override"}})')
  proc=subprocess.Popen(['/tmp/pixel-doom-foot-build/foot','--config=/dev/null',f'--server={sock}',
       '-o','font=monospace:size=2','-o','workers=0','-o','pad=0x0','-o','resize-by-cells=no',
       '-o','tweak.font-monospace-warn=no'],env=os.environ|{'FOOT_PIXEL_DOOM':'1'},stdout=log,stderr=log)
  wait_for(lambda:sock.exists())
  for i in range(32):
   color=colors[i%len(colors)]
   escape='\033[?25l\033[2J\033]11;#%02x%02x%02x\a'%color
   child=f"import sys,time; from pathlib import Path; p=Path({str(update)!r}); sys.stdout.write({escape!r});sys.stdout.flush()\nlast=''\nwhile True:\n value=p.read_text()\n if value!=last:\n  sys.stdout.write(value or {escape!r});sys.stdout.flush();last=value\n time.sleep(.05)"
   open_window(sock,app,f'cell-{i}',50,40,[sys.executable,'-c',child],True)
  clients=lambda:[w for w in h.request('clients',True) if w['class']==app]
  wait_for(lambda:len(clients())==32)
  windows={int(w['title'].split('-')[-1]):w for w in clients()}
  for i,w in windows.items():
   h.run(f'hl.dsp.window.move({{window="address:{w["address"]}",x={20+i%8*65},y={40+i//8*60}}})')
  time.sleep(.3)
  def capture(name):
   path=out/name
   subprocess.run(['grim',str(path)],check=True,timeout=10)
   width=int(subprocess.check_output(['magick','identify','-format','%w',str(path)]))
   pixels=subprocess.check_output(['magick',str(path),'-depth','8','rgb:-'])
   return width,pixels
  def check(img,x,y,expected):
   width,pixels=img
   offset=(y*width+x)*3
   actual=tuple(pixels[offset:offset+3])
   assert max(abs(a-b) for a,b in zip(actual,expected))<=2,(x,y,actual,expected)
  img=capture('colors.png')
  for i in windows:check(img,45+i%8*65,60+i//8*60,colors[i%len(colors)])
  # Force the ordinary renderer without changing the committed pixel buffers.
  # Shared textures must retain the right colors when batching is ineligible.
  h.request('eval hl.config({decoration={blur={enabled=true}}})')
  time.sleep(.3)
  img=capture('normal-renderer-colors.png')
  for i in windows:check(img,45+i%8*65,60+i//8*60,colors[i%len(colors)])
  h.request('eval hl.config({decoration={blur={enabled=false}}})')
  update.write_text('\033[38;2;255;255;255mTEXT FALLBACK');time.sleep(.3)
  img=capture('text-fallback.png')
  # The first window is red: white glyphs must add green and blue there.
  imgwidth,raw=img
  assert any(raw[(y*imgwidth+x)*3+1]>10 and raw[(y*imgwidth+x)*3+2]>10
             for y in range(40,80) for x in range(20,70)), 'Text was not rendered'
  update.write_text('\033[2J\033]11;#123456\a');time.sleep(.3)
  img=capture('after-text-colors.png')
  for i in windows:check(img,45+i%8*65,60+i//8*60,(18,52,86))
  update.write_text('\033]11;#123456\a');time.sleep(.3)
  img=capture('updated-colors.png')
  for i in windows:check(img,45+i%8*65,60+i//8*60,(18,52,86))
  h.request('eval hl.config({decoration={blur={enabled=true}}})')
  time.sleep(.3)
  img=capture('updated-normal-renderer.png')
  for i in windows:check(img,45+i%8*65,60+i//8*60,(18,52,86))
  h.request('eval hl.config({decoration={blur={enabled=false}}})')
  update.write_text('');time.sleep(.3)
  a,b=windows[0]['address'],windows[1]['address']
  h.run(f'hl.dsp.window.move({{window="address:{b}",x=20,y=40}})',f'hl.dsp.window.resize({{window="address:{b}",x=80,y=50}})')
  time.sleep(.2)
  h.run(f'hl.dsp.window.move({{window="address:{b}",x=20,y=40}})')
  h.focus(b);time.sleep(.2)
  img=capture('stack-resize.png');check(img,25,45,colors[1]);check(img,95,45,colors[1])
  count_rule=rule+'_count'
  h.request(f'eval {count_rule}=hl.window_rule({{name="{count_rule}",match={{class="^{app}$",workspace="w[31]"}},border_size=3}})')
  assert h.request(f'getprop address:{a} border_size',True)['border_size']==0
  h.run(f'hl.dsp.window.close({{window="address:{b}"}})')
  wait_for(lambda:len(clients())==31);time.sleep(.2)
  wait_for(lambda:h.request(f'getprop address:{a} border_size',True)['border_size']==3)
  img=capture('after-close.png');check(img,45,60,colors[0])
  h.request(f'eval {count_rule}:set_enabled(false)')
  wait_for(lambda:h.request(f'getprop address:{a} border_size',True)['border_size']==0)
  print('PASS: colors, updates, renderer/text fallback, stacking, resize, close reveal, population-dependent rules and removal',flush=True)
 finally:
  stop(proc)
  wait_for(lambda:not [w for w in h.request('clients',True) if w['class']==app])
  h.request(f'eval if {rule} then {rule}:set_enabled(false); {rule}=nil end')
  h.request(f'eval if {rule}_count then {rule}_count:set_enabled(false); {rule}_count=nil end')

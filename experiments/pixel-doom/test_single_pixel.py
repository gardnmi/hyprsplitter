"""One small, unfocused window: verify 1x1 -> text -> 1x1 rendering."""
import os
from pathlib import Path
import re
import subprocess
import sys
import time
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from hyprsplitter import Hyprland

h=Hyprland(); app=f"pixel-doom-check-{os.getpid()}"; rule=f"pixel_check_{os.getpid()}"
out=Path(__file__).with_name('output'); out.mkdir(exist_ok=True)
geometry='--cache-pixel-geometry' in sys.argv
cache='--color-buffer-cache' in sys.argv
no_callback='--no-pixel-frame-callback' in sys.argv
suffix=('cache' if cache else 'shm')+('-no-callback' if no_callback else '')+('-geometry' if geometry else '')
log=out/f'single-pixel-{suffix}-protocol.log'
command="import sys,time;sys.stdout.write('\\x1b[?25l\\x1b[2J\\x1b]11;#800000\\x07');sys.stdout.flush();time.sleep(2);print('TEXT FALLBACK',flush=True);time.sleep(3);sys.stdout.write('\\x1b[2J\\x1b]11;#008000\\x07');sys.stdout.flush();time.sleep(2)"
h.request(f'eval {rule}=hl.window_rule({{name="{rule}",match={{class="^{app}$"}},float=true,no_anim=true,no_initial_focus=true,size={{320,180}},move={{20,60}}}})')
proc=None
try:
    with log.open('w') as f:
        proc=subprocess.Popen(['/tmp/pixel-doom-foot-build/foot','--config=/dev/null','-a',app,
            '-T','Single-pixel rendering check','-o','workers=0',sys.executable,'-c',command],
            env={**{k:v for k,v in os.environ.items() if k not in ('FOOT_PIXEL_DOOM_CACHE','FOOT_PIXEL_DOOM_NO_CALLBACK')},
                 **({'FOOT_PIXEL_DOOM_CACHE':'1'} if cache else {}),
                 **({'FOOT_PIXEL_DOOM_NO_CALLBACK':'1'} if no_callback else {}),
                 **({'FOOT_PIXEL_DOOM_CACHE_GEOMETRY':'1'} if geometry else {}),
                 'FOOT_PIXEL_DOOM':'1','WAYLAND_DEBUG':'client'},stdout=f,stderr=f)
        time.sleep(3.5)
        windows=[w for w in h.request('clients',True) if w['class']==app]
        if len(windows)!=1: raise RuntimeError('Test window did not appear')
        w=windows[0]; x,y=w['at']; width,height=w['size']
        subprocess.run(['grim','-g',f'{x},{y} {width}x{height}',str(out/f'single-pixel-{suffix}-text-fallback.png')],check=True)
        if geometry:
            time.sleep(2.2)
            h.run(f'hl.dsp.window.resize({{window="address:{w["address"]}",x=360,y=200}})')
        if proc.wait(timeout=8): raise RuntimeError('Foot failed')
    sizes=[]
    for line in log.read_text().splitlines():
        if 'create_u32_rgba_buffer(' in line:
            sizes.append((1,1))
        else:
            m=re.search(r'create_buffer\(new id [^,]+, \d+, (\d+), (\d+),',line)
            if m: sizes.append(tuple(map(int,m.groups())))
    if geometry:
        assert any('.set_destination(360, 200)' in line for line in log.read_text().splitlines()), 'Missing resized viewport'
    first=sizes.index((1,1))
    normal=next(i for i in range(first+1,len(sizes)) if sizes[i][0]>1 and sizes[i][1]>1)
    assert (1,1) in sizes[normal+1:], sizes
    if no_callback:
        lines=log.read_text().splitlines()
        first_pixel=next(i for i,line in enumerate(lines) if 'create_buffer(' in line and re.search(r', 1, 1,',line))
        text_buffer=next(i for i in range(first_pixel+1,len(lines)) if 'create_buffer(' in lines[i] and not re.search(r', 1, 1,',lines[i]))
        assert not any('.frame(' in line for line in lines[first_pixel:text_buffer]), 'Unexpected blank-frame callback'
        assert any('.frame(' in line for line in lines[text_buffer:]), 'Text must restore normal frame callbacks'
    if cache: assert 'create_u32_rgba_buffer(' in log.read_text()
    print('PASS:',suffix,'1x1 buffer, full-size text buffer, then 1x1 again:',sizes)
finally:
    if proc and proc.poll() is None: proc.terminate();proc.wait(timeout=5)
    h.request(f'eval if {rule} then {rule}:set_enabled(false);{rule}=nil end')

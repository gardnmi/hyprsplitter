"""Readable real-terminal proof and live window-count prelude for recordings."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time

from foot_ipc import open_window


class Intro:
    def __init__(self, h, foot, tmp, workspace, monitor, app, target, log, procs):
        self.h, self.app, self.target = h, app+'-proof', target
        self.path=tmp/'intro-status.json'
        self.rule='proof_'+str(os.getpid())
        self.address=None
        self.server=None
        self.update(0,'These are real Foot terminals')
        width=int(monitor['width']/monitor['scale'])
        height=int(monitor['height']/monitor['scale'])
        self.x,self.y=monitor['x'],monitor['y']
        pane_w,pane_h=min(460,(width-60)//2),min(240,(height-80)//2)
        h.request(f'eval {self.rule}=hl.window_rule({{name="{self.rule}",match={{class="^{self.app}$"}},workspace="{workspace} silent",float=true,no_anim=true,no_initial_focus=true,border_size=2,rounding=0,no_shadow=true,no_blur=true,size={{{pane_w},{pane_h}}}}})')
        sock=tmp/'intro-foot.sock'
        try:
            self.server=subprocess.Popen([foot,'--config=/dev/null',f'--server={sock}',
                '-o','font=monospace:size=12','-o','pad=12x12','-o','workers=0',
                '-o','tweak.font-monospace-warn=no','-o','colors-dark.background=080c10'],
                stdout=log,stderr=log,start_new_session=True)
            procs.append(self.server)
            deadline=time.monotonic()+5
            while not sock.exists():
                if self.server.poll() is not None or time.monotonic()>deadline:
                    raise RuntimeError('Intro Foot server did not start')
                time.sleep(.02)
            h.run(f'hl.dsp.focus({{workspace="{workspace}"}})')
            for i in range(4):
                open_window(sock,self.app,f'REAL TERMINAL {i+1}',pane_w,pane_h,
                    [sys.executable,str(Path(__file__).resolve()),'pane',str(i),str(self.path)],False)
            deadline=time.monotonic()+5
            while True:
                windows=[w for w in h.request('clients',True) if w['class']==self.app]
                if len(windows)==4:break
                if time.monotonic()>deadline:raise RuntimeError('Intro windows did not appear')
                time.sleep(.05)
            for w in windows:
                i=int(w['title'].split()[-1])-1
                h.run(f'hl.dsp.window.move({{window="address:{w["address"]}",x={self.x+20+(i%2)*(pane_w+12)},y={self.y+30+(i//2)*(pane_h+12)}}})')
                if i==0:self.address=w['address']
            time.sleep(4)
            self.update(0,'Opening the mosaic',compact=True)
            h.run(f'hl.dsp.window.resize({{window="address:{self.address}",x={min(460,width-40)},y=150}})')
        except BaseException:
            self.close()
            raise

    def update(self,count,stage='Opening the mosaic',compact=False):
        self.path.write_text(json.dumps(dict(count=count,target=self.target,stage=stage,compact=compact)))
        if self.address:
            self.h.focus(self.address)

    def finish(self,count):
        self.update(count,'Starting DOOM',compact=True)
        time.sleep(2)
        self.close()

    def close(self):
        if self.server is not None and self.server.poll() is None:
            self.server.terminate()
            try:self.server.wait(timeout=5)
            except subprocess.TimeoutExpired:self.server.kill();self.server.wait()
        try:self.h.request(f'eval if {self.rule} then {self.rule}:set_enabled(false); {self.rule}=nil end')
        except (OSError,RuntimeError):pass


def pane(index,path):
    tty=os.ttyname(0)
    print('\033[?25l',end='',flush=True)
    old=None
    while True:
        try:state=json.loads(path.read_text())
        except (FileNotFoundError,json.JSONDecodeError):time.sleep(.05);continue
        if state.get('compact') and index:return
        if state!=old:
            print('\033[2J\033[H',end='')
            if state.get('compact'):
                print('\033[1;36mREAL TERMINAL WINDOWS\033[0m')
                print(f"{state['count']:,} / {state['target']:,}")
                print(state['stage'])
            else:
                print(f'\033[1;36mFOOT TERMINAL {index+1}\033[0m\n')
                print('TTY: '+tty)
                print('Process: '+str(os.getpid()))
                print('\nIdentity preview. Not in mosaic count.')
            sys.stdout.flush();old=state
        time.sleep(.1)


if __name__=='__main__':
    pane(int(sys.argv[2]),Path(sys.argv[3]))

#!/usr/bin/env python3
"""Two real Hyprland windows: move a rain cloud to extinguish a fire."""
import argparse,json,math,os,signal,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from hyprsplitter import Hyprland
import gi
gi.require_version('Gtk','3.0')
gi.require_version('Gdk','3.0')
gi.require_version('GLibUnix','2.0')
from gi.repository import Gtk,Gdk,GLib,GLibUnix
import cairo


def rain_hits(cloud,fire):
    """World-space rain column intersects fire cells on the same workspace."""
    if not cloud or not fire or cloud['workspace']['id']!=fire['workspace']['id']:
        return [False]*12
    cx,cy=cloud['at'];cw,ch=cloud['size'];fx,fy=fire['at'];fw,fh=fire['size']
    above=cy+ch*.5<fy and -70<=fy-(cy+ch)<=850
    left,right=cx+cw*.14,cx+cw*.86
    return [above and left<=fx+fw*(.22+i*.56/11)<=right for i in range(12)]


def text(cr,s,x,y,size=14,color=(.7,.77,.85)):
    cr.set_source_rgb(*color);cr.select_font_face('sans-serif',cairo.FONT_SLANT_NORMAL,cairo.FONT_WEIGHT_NORMAL)
    cr.set_font_size(size);cr.move_to(x,y);cr.show_text(s)


def circle(cr,x,y,r,color):
    cr.set_source_rgba(*color);cr.arc(x,y,r,0,math.tau);cr.fill()


class Demo:
    def __init__(self,state_file):
        self.hypr=Hyprland();self.prefix=f'RainFire-{os.getpid()}';self.rule=f'rain_fire_{os.getpid()}'
        self.windows={};self.areas={};self.geometry={};self.heat=[1.]*12;self.wet=[False]*12
        self.won=False;self.closed=False;self.ready=False;self.last=time.monotonic();self.state_file=state_file
        self.started=self.last;self.initial=None;self.error=None
        monitor=next(m for m in self.hypr.request('monitors',True) if m['focused'])
        mw,mh=monitor['width']/monitor['scale'],monitor['height']/monitor['scale']
        fx=int(monitor['x']+mw*.53-220);fy=int(monitor['y']+mh*.53)
        self.initial={'cloud':(max(int(monitor['x'])+25,fx-410),max(int(monitor['y'])+50,fy-310)),'fire':(fx,fy)}
        self.hypr.request(f'eval {self.rule}=hl.window_rule({{name="{self.rule}",match={{initial_title="^{self.prefix}-.*$"}},float=true,no_anim=true,border_size=2,rounding=18,opacity="1 override 1 override"}})')
        try:
            for role,size in [('fire',(520,330)),('cloud',(420,250))]:
                win=Gtk.Window(title=f'{self.prefix}-{role}');win.set_decorated(False);win.set_default_size(*size)
                win.connect('delete-event',lambda *_:self.close());win.connect('key-press-event',self.key)
                area=Gtk.DrawingArea();area.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
                area.connect('button-press-event',lambda widget,event,w=win:self.drag(w,event))
                area.connect('draw',lambda widget,cr,r=role:self.draw(r,widget,cr))
                win.add(area);win.show_all();self.windows[role]=win;self.areas[role]=area
            GLib.timeout_add(100,self.sync);GLib.timeout_add(33,self.tick)
            GLibUnix.signal_add(GLib.PRIORITY_DEFAULT,signal.SIGTERM,self.close)
            GLibUnix.signal_add(GLib.PRIORITY_DEFAULT,signal.SIGINT,self.close)
        except BaseException:
            self.close();raise

    def drag(self,win,event):
        if event.button==1:win.begin_move_drag(1,int(event.x_root),int(event.y_root),event.time)
        return True

    def key(self,win,event):
        key=Gdk.keyval_name(event.keyval).lower()
        if key=='escape':self.close()
        if key=='r':self.heat=[1.]*12;self.won=False
        return key in ('escape','r')

    def sync(self):
        if self.closed:return False
        try:
            clients=self.hypr.request('clients',True)
            self.geometry={role:next((c for c in clients if c.get('initialTitle')==f'{self.prefix}-{role}'),None) for role in self.windows}
            if not all(self.geometry.values()):
                if self.ready:self.close();return False
                if time.monotonic()-self.started>10:raise RuntimeError('Windows did not appear')
                return True
            if not self.ready:
                for role,c in self.geometry.items():
                    x,y=self.initial[role];w,h=(420,250) if role=='cloud' else (520,330)
                    sel=json.dumps('address:'+c['address'])
                    self.hypr.run(f'hl.dsp.window.resize({{window={sel},x={w},y={h}}})',f'hl.dsp.window.move({{window={sel},x={x},y={y}}})')
                self.ready=True
                print('READY: drag cloud above fire. R resets; Esc closes both.',flush=True)
            else:self.wet=rain_hits(self.geometry.get('cloud'),self.geometry.get('fire'))
            if self.state_file:
                state={'pid':os.getpid(),'prefix':self.prefix,'ready':self.ready,'heat':self.heat,'wet':self.wet,'won':self.won,
                       'windows':{k:{p:v[p] for p in ('address','at','size')} for k,v in self.geometry.items()}}
                self.state_file.write_text(json.dumps(state)+'\n')
        except Exception as e:
            self.error=str(e);print(f'ERROR: {e}',file=sys.stderr,flush=True);self.close();return False
        return True

    def tick(self):
        if self.closed:return False
        now=time.monotonic();dt=min(.1,now-self.last);self.last=now
        if self.ready and not self.won:
            self.heat=[max(0.,h-.32*dt) if wet else min(1.,h+.045*dt) for h,wet in zip(self.heat,self.wet)]
            if max(self.heat)<.015:self.heat=[0.]*12;self.won=True
        for area in self.areas.values():area.queue_draw()
        return True

    def draw(self,role,widget,cr):
        w,h=widget.get_allocated_width(),widget.get_allocated_height();t=time.monotonic()-self.started
        gradient=cairo.LinearGradient(0,0,0,h)
        gradient.add_color_stop_rgb(0,.055,.075,.12);gradient.add_color_stop_rgb(1,.025,.035,.065)
        cr.set_source(gradient);cr.paint()
        text(cr,'WEATHER / 01' if role=='cloud' else 'WILDFIRE / 02',22,30,11,(.4,.63,.76))
        text(cr,'DRAG ME' if role=='cloud' else 'R TO RESET  /  ESC TO CLOSE',w-(90 if role=='cloud' else 226),30,10)
        if role=='cloud':
            self.draw_cloud(cr,w,h,t)
        else:self.draw_fire(cr,w,h,t)
        return False

    def drops(self,cr,w,top,bottom,t,mask=None):
        cr.set_line_width(2);cr.set_line_cap(cairo.LINE_CAP_ROUND)
        for i in range(38):
            fraction=.14+.72*((i*0.61803398875)%1)
            x=w*fraction;y=top+((t*175+i*37)%(max(1,bottom-top)))
            if mask and not mask(x):continue
            cr.set_source_rgba(.30,.73,1.,.35+.45*(i%3)/2)
            cr.move_to(x,y);cr.line_to(x-3,y+11);cr.stroke()

    def draw_cloud(self,cr,w,h,t):
        self.drops(cr,w,124,h-43,t)
        glow=cairo.RadialGradient(w*.5,110,8,w*.5,110,150)
        glow.add_color_stop_rgba(0,.2,.6,.9,.20);glow.add_color_stop_rgba(1,.1,.3,.8,0)
        cr.set_source(glow);cr.rectangle(0,38,w,h-76);cr.fill()
        bob=math.sin(t*1.5)*3
        for x,y,r in [(.33,107,32),(.44,85,41),(.56,86,47),(.67,108,33),(.50,112,44)]:
            circle(cr,w*x,y+bob,r,(.75,.85,.94,1))
        cr.set_source_rgb(.75,.85,.94);cr.rectangle(w*.32,106+bob,w*.35,28);cr.fill()
        circle(cr,w*.46,107+bob,3,(.10,.20,.30,1));circle(cr,w*.55,107+bob,3,(.10,.20,.30,1))
        cr.set_source_rgb(.1,.2,.3);cr.set_line_width(2);cr.arc(w*.505,112+bob,8,.2,math.pi-.2);cr.stroke()
        msg='Nice! Keep the rain over the flames.' if any(self.wet) else 'Drag this cloud above the fire window.'
        if self.won:msg='Fire out. A little rain goes a long way.'
        text(cr,msg,22,h-20,13,(.64,.83,.94))

    def draw_fire(self,cr,w,h,t):
        wet=any(self.wet);average=sum(self.heat)/len(self.heat)
        if wet and self.geometry.get('cloud') and self.geometry.get('fire'):
            c,f=self.geometry['cloud'],self.geometry['fire'];left=c['at'][0]+c['size'][0]*.14-f['at'][0];right=c['at'][0]+c['size'][0]*.86-f['at'][0]
            # Match the cloud's rain column in desktop coordinates.
            cr.save();cr.rectangle(max(0,left),48,max(0,min(w,right)-max(0,left)),h-112);cr.clip()
            self.drops(cr,w,48,h-64,t+1);cr.restore()
        glow=cairo.RadialGradient(w*.5,h-89,3,w*.5,h-89,w*.43)
        glow.add_color_stop_rgba(0,1,.23,.025,.25*average);glow.add_color_stop_rgba(1,1,.13,0,0)
        cr.set_source(glow);cr.rectangle(0,40,w,h-75);cr.fill()
        cr.set_source_rgb(.16,.12,.10);cr.set_line_width(13);cr.set_line_cap(cairo.LINE_CAP_ROUND)
        cr.move_to(w*.22,h-79);cr.line_to(w*.78,h-66);cr.move_to(w*.23,h-65);cr.line_to(w*.77,h-81);cr.stroke()
        for i,fuel in enumerate(self.heat):
            x=w*(.22+i*.56/11);base=h-80
            if fuel>.01:
                height=(95+35*math.sin(i*2.7+t*8))*fuel;lean=math.sin(t*5+i)*12
                for scale,color in [(1,(1,.23,.04,.92)),(.68,(1,.56,.07,.98)),(.36,(1,.9,.39,1))]:
                    hh=height*scale;radius=(13+fuel*7)*scale
                    cr.set_source_rgba(*color);cr.move_to(x-radius,base)
                    cr.curve_to(x-radius*2,base-hh*.5,x+lean-radius,base-hh*.85,x+lean,base-hh)
                    cr.curve_to(x+lean-2,base-hh*.45,x+radius*2,base-hh*.35,x+radius,base);cr.close_path();cr.fill()
            if self.wet[i] or self.won:
                for j in range(2):
                    age=(t*.7+i*.13+j*.5)%1
                    circle(cr,x+math.sin(t+i+j)*8,base-30-age*100,5+age*13,(.68,.81,.86,(1-age)*.23))
        bar_y=h-43
        cr.set_source_rgb(.12,.17,.22);cr.rectangle(22,bar_y,w-44,5);cr.fill()
        cr.set_source_rgb(*((.3,.78,.91) if wet else (1,.38,.12)));cr.rectangle(22,bar_y,(w-44)*average,5);cr.fill()
        msg='EXTINGUISHED!  Press R to relight.' if self.won else ('Rain is working — keep it here!' if wet else 'Move the cloud above me to put me out.')
        text(cr,msg,22,h-17,13,(.6,.89,.94) if wet or self.won else (.95,.7,.46))

    def close(self):
        if self.closed:return False
        self.closed=True
        for win in self.windows.values():win.destroy()
        try:self.hypr.request(f'eval if {self.rule} then {self.rule}:set_enabled(false); {self.rule}=nil end')
        except Exception:pass
        Gtk.main_quit();return False


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--state-file',type=Path);args=p.parse_args()
    GLib.set_prgname('rain-fire-poc')
    demo=Demo(args.state_file)
    try:Gtk.main()
    finally:demo.close()
    if demo.error:raise SystemExit(demo.error)

if __name__=='__main__':main()

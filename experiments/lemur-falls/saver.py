"""Read complete animation frames from Omarchy's actual ttfx engine."""
import os,re,subprocess,codecs
from pathlib import Path

ANSI=re.compile(r'\x1b\[([0-9;?]*)([A-Za-z])|\x1b[78]')
class Saver:
 def __init__(self):
  self.proc=None;self.buffer='';self.cells=[];self.effect=0;self.decoder=codecs.getincrementaldecoder('utf8')()
  self.source=Path.home()/'.config/omarchy/branding/screensaver.txt'
  if not self.source.exists():self.source=Path('/usr/share/omarchy/logo.txt')
  self.start()
 def start(self):
  effects=('rain','pour','fireworks','waves','beams')
  self.proc=subprocess.Popen(['ttfx','-i',str(self.source),'--canvas-width','90','--canvas-height','18','--ignore-terminal-dimensions','--frame-rate','30','--anchor-text','c','--no-eol','--no-restore-cursor',effects[self.effect%len(effects)]],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
  os.set_blocking(self.proc.stdout.fileno(),False);self.effect+=1;self.buffer='';self.decoder.reset()
 def poll(self):
  while True:
   try:data=os.read(self.proc.stdout.fileno(),65536)
   except BlockingIOError:break
   if not data:break
   self.buffer+=self.decoder.decode(data)
  # ttfx restores its saved cursor after each complete canvas.
  if '\x1b8' in self.buffer:
   frames=self.buffer.split('\x1b8');self.buffer=frames[-1];self.parse(frames[-2])
  if self.proc.poll() is not None:
   self.proc.stdout.close();self.start()
 def parse(self,frame):
  cells=[];row=col=0;color=(.86,.84,.73);pos=0
  def literal(txt):
   nonlocal row,col
   for ch in txt:
    if ch=='\n':row+=1;col=0
    elif ch=='\r':col=0
    else:
     if ch!=' ' and row<18:cells.append((col,row,ch,color))
     col+=1
  for match in ANSI.finditer(frame):
   literal(frame[pos:match.start()]);args,cmd=match.groups()
   if cmd=='A':row=col=0
   elif cmd=='m':
    values=[int(v) for v in args.split(';') if v.isdigit()]
    if values[:2]==[38,2] and len(values)>=5:color=tuple(v/255 for v in values[2:5])
    elif not values or values==[0]:color=(.86,.84,.73)
   pos=match.end()
  literal(frame[pos:]);self.cells=cells
 def close(self):
  if self.proc and self.proc.poll() is None:
   self.proc.terminate()
   try:self.proc.wait(timeout=1)
   except subprocess.TimeoutExpired:self.proc.kill();self.proc.wait()
  if self.proc and self.proc.stdout:self.proc.stdout.close()

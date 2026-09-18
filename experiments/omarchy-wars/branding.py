"""Render the installed Omarchy block wordmark without font-dependent glyphs."""
from pathlib import Path
try:LOGO=Path('/usr/share/omarchy/logo.txt').read_text().splitlines()
except OSError:LOGO=[' ███ ','██ ██','██ ██',' ███ ']

def wordmark(c,x,y,w,h):
 cols=max(map(len,LOGO));cw=w/cols;ch=h/len(LOGO)
 for row,line in enumerate(LOGO):
  for col,char in enumerate(line):
   if char==' ':continue
   c.set_source_rgb(*((.75,.78,.96) if row<2 else (.47,.80,.96) if row<8 else (.5,.6,.93)))
   offset=.5 if char=='▄' else 0;fraction=.5 if char in '▄▀' else 1
   c.rectangle(x+col*cw,y+(row+offset)*ch,cw+.2,ch*fraction+.2);c.fill()

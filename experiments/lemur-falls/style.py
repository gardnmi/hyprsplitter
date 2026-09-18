"""Shared visual language for Road to OMACON; no desktop settings changed."""
from experiments.theme import rgb as theme_rgb
FONT='monospace'
PAD=12
TITLE_SIZE=11
HINT_SIZE=10

def rgb(name):
 # Keep the installed Omarchy palette, with legible secondary copy everywhere.
 if name=='muted':
  fg=theme_rgb('foreground');bg=theme_rgb('dark_background')
  return tuple(b+(f-b)*.57 for b,f in zip(bg,fg))
 return theme_rgb(name)

def text(c,s,x,y,size=12,color='foreground'):
 c.save();c.set_source_rgb(*rgb(color));c.select_font_face(FONT,0,0);c.set_font_size(size);c.move_to(x,y);c.show_text(s);c.restore()

def panel(c,w,h,accent='green'):
 c.set_source_rgb(*rgb('dark_background'));c.paint()
 c.set_source_rgba(*rgb('foreground'),.22);c.set_line_width(1)
 c.rectangle(.5,.5,w-1,h-1);c.stroke()
 # A single short accent, not an ornamental pattern or extra title bar.
 c.set_source_rgb(*rgb(accent));c.rectangle(1,1,24,2);c.fill()

def heading(c,label,accent='green'):
 text(c,label,PAD,23,TITLE_SIZE,accent)

def hint(c,label,h,accent='muted'):
 text(c,label,PAD,h-6,HINT_SIZE,accent)

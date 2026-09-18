"""A Waybar-like carriage and real Omarchy bar glyphs."""
import math,cairo
from style import text,rgb,panel,heading
# Installed Omarchy Caldir BarWidget and StayAwake indicator glyphs.
ICONS={'plugin2':'󰃲','plugin3':'󰅶'}
def icon(c,glyph,x,y,size=22,color='foreground',alpha=1):
 c.save();c.set_source_rgba(*rgb(color),alpha);c.select_font_face('Symbols Nerd Font',0,0);c.set_font_size(size);c.move_to(x,y);c.show_text(glyph);c.restore()
def line(c,points,color='cyan',width=2):
 c.set_source_rgb(*rgb(color));c.set_line_width(width);c.move_to(*points[0])
 for p in points[1:]:c.line_to(*p)
 c.stroke()
def draw_piece(c,w,h,role,j,colony,t):
 if role in ICONS:
  panel(c,w,h,'bright_green' if role in j.docked else 'foreground')
  icon(c,ICONS[role],w/2-11,h/2+8,color='bright_green' if role in j.docked else 'foreground')
 elif role.startswith('plugin'):
  panel(c,w,h,'cyan');heading(c,'BRIDGE '+str(int(role[-1])+1),'cyan')
  text(c,'DRAG TO CONNECT',12,39,10,'muted');line(c,[(0,h-20),(w,h-20)],'cyan',3)
  for x in (4,w-4):
   c.set_source_rgba(*rgb('cyan'),.5+.25*math.sin(t*3));c.rectangle(x-3,h-26,6,12);c.fill()
 else:
  c.set_operator(cairo.OPERATOR_CLEAR);c.paint();c.set_operator(cairo.OPERATOR_OVER)
  floor=j.lift()[1]-j.rects[role][1];bottom=h-110
  for x in (5,w-5):
   c.set_source_rgba(*rgb('foreground'),.16);c.set_line_width(1);c.set_dash([2,8]);c.move_to(x,170);c.line_to(x,bottom);c.stroke();c.set_dash([])
  c.save();c.translate(0,floor-34);c.rectangle(0,0,w,38);c.clip();panel(c,w,38,'foreground')
  # Familiar workspace numbers, time/level in the middle, plugin status on the right.
  text(c,'1  2  3',12,22,11,'muted');text(c,'UP' if j.progress>.99 else 'LIFT',w/2-18,22,11)
  for i,name in enumerate(ICONS):icon(c,ICONS[name],w-65+i*30,24,18,'bright_green' if name in j.docked else 'muted')
  line(c,[(0,34),(w,34)],'foreground',2);c.restore()
  for i,(sx,sy) in enumerate(j.sockets()):
   x=sx-j.rects[role][0];y=sy-j.rects[role][1]
   c.set_source_rgba(*rgb('dark_background'),.95);c.rectangle(x-29,y-20,58,40);c.fill()
   c.set_source_rgba(*rgb('foreground'),.35);c.set_line_width(1);c.set_dash([3,3]);c.rectangle(x-28,y-19,56,38);c.stroke();c.set_dash([])
   icon(c,list(ICONS.values())[i],x-10,y+7,20,'muted',.45)
  text(c,'DOCK ICONS TO RAISE',w/2-62,h-91,10,'muted')

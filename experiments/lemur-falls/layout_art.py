"""Restrained route markers behind the real gameplay windows."""
import math
from style import text,rgb
from layout import objective

def draw_route(c,app,t):
 mx,my=app.mx,app.my;w,h=app.mw,app.mh
 title,detail=objective(app)
 text(c,'ROAD TO OMACON',60,58,18)
 text(c,title,540,55,12,'bright_green')
 text(c,detail,540,77,10,'muted')
 # Short directional hints between stages, deliberately distinct from solid floors.
 def arrow(points):
  c.set_source_rgba(*rgb('foreground'),.19);c.set_line_width(1.5);c.set_dash([3,8]);c.move_to(*points[0])
  for point in points[1:]:c.line_to(*point)
  c.stroke();c.set_dash([])
  (ax,ay),(bx,by)=points[-2:];angle=math.atan2(by-ay,bx-ax)
  c.move_to(bx-9*math.cos(angle-.5),by-9*math.sin(angle-.5));c.line_to(bx,by);c.line_to(bx-9*math.cos(angle+.5),by-9*math.sin(angle+.5));c.stroke()
 cx,cy,cw,ch=app.catcher;gx,gy,gw,gh=app.gate
 arrow([(cx-mx+40,cy-my+ch+16),(cx-mx-30,gy-my-25)])
 text(c,'02 / CHAIR CRASH',gx-mx+12,gy-my-16,10,'muted')
 ex,ey,ew,eh=app.journey.rects['elevator']
 text(c,'03 / PLUGIN LIFT',ex-mx+12,ey-my+110,10,'muted')
 text(c,'04 / OMACON',app.goal[0]-mx+12,app.goal[1]-my-12,10,'muted')

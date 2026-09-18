"""Code-drawn retro hardware and animated cartridge illustrations."""
import math
import cairo
from experiments.theme import rgb,mix

def color(c,name,alpha=1):c.set_source_rgba(*rgb(name),alpha)
def box(c,x,y,w,h,name):color(c,name);c.rectangle(x,y,w,h);c.fill()
def text(c,s,x,y,size=12,name='foreground'):
 color(c,name);c.select_font_face('monospace',cairo.FONT_SLANT_NORMAL,cairo.FONT_WEIGHT_BOLD);c.set_font_size(size);c.move_to(x,y);c.show_text(s)
def roundbox(c,x,y,w,h,r,name):
 c.new_sub_path()
 for xx,yy,start in ((x+w-r,y+r,-math.pi/2),(x+w-r,y+h-r,0),(x+r,y+h-r,math.pi/2),(x+r,y+r,math.pi)):
  c.arc(xx,yy,r,start,start+math.pi/2)
 c.close_path();color(c,name);c.fill()
def screw(c,x,y):
 c.new_path()
 color(c,'muted');c.arc(x,y,3,0,math.tau);c.fill();color(c,'dark_background');c.set_line_width(1);c.move_to(x-2,y);c.line_to(x+2,y);c.stroke()
def illustration(c,game,t):
 # All labels share one print frame and ink palette; artwork differs per game.
 box(c,0,0,170,110,'dark_background')
 if game=='space':
  for i in range(22):
   x=(i*71%170-t*4)%170;y=i*37%110
   color(c,'foreground',.2+.4*(.5+.5*math.sin(t+i)));c.rectangle(x,y,1.5,1.5);c.fill()
  c.save();c.translate(85,53+math.sin(t*2)*3)
  color(c,'cyan');c.move_to(0,-28);c.line_to(22,21);c.line_to(0,12);c.line_to(-22,21);c.close_path();c.fill()
  box(c,-4,-7,8,18,'foreground');color(c,'orange');c.move_to(-7,19);c.line_to(0,32+math.sin(t*13)*4);c.line_to(7,19);c.fill();c.restore()
 elif game=='zero':
  c.save();c.translate(85,53);c.set_source_rgb(*rgb('blue'));c.set_line_width(10);c.rectangle(-18,-29,36,58);c.stroke();c.set_source_rgb(*rgb('cyan'));c.set_line_width(2)
  for i in range(4):
   x=(t*28+i*35)%170-85;c.move_to(x,0);c.line_to(x+10,0);c.stroke()
  c.restore()
 elif game=='quattro':
  g=cairo.LinearGradient(0,0,0,110);g.add_color_stop_rgb(0,.19,.08,.22);g.add_color_stop_rgb(1,.65,.23,.27);c.set_source(g);c.paint()
  color(c,'bright_yellow');c.arc(124,36,26,0,math.tau);c.fill()
  for y in range(37,63,6):box(c,97,y,55,2,'orange')
  color(c,'dark_background');c.move_to(0,98);c.line_to(170,73);c.line_to(170,110);c.line_to(0,110);c.fill()
  c.save();c.translate(77,75+math.sin(t*2)*2);c.rotate(-.16)
  box(c,-44,-16,87,20,'foreground');color(c,'foreground');c.move_to(-28,-16);c.line_to(-15,-34);c.line_to(16,-34);c.line_to(31,-16);c.fill()
  box(c,-14,-30,27,12,'dark_background');box(c,-44,-11,85,4,'red');box(c,32,-14,10,6,'bright_yellow')
  for x in (-26,25):
   color(c,'dark_background');c.arc(x,5,10,0,math.tau);c.fill();color(c,'muted');c.arc(x,5,5,0,math.tau);c.fill()
  c.restore()
 elif game=='tux':
  for i in range(9):box(c,i*22,90-i%3*7,17,20,'green')
  c.save();c.translate(85,55+math.sin(t*2)*2)
  def oval(x,y,rx,ry,name):
   c.save();c.translate(x,y);c.scale(rx,ry);color(c,name);c.arc(0,0,1,0,math.tau);c.fill();c.restore()
  oval(-15,30,13,5,'yellow');oval(15,30,13,5,'yellow');oval(0,0,23,35,'background');oval(0,9,17,23,'foreground')
  for x in (-8,8):oval(x,-15,6,8,'foreground');oval(x+1,-14,2,4,'dark_background')
  oval(0,-3,12,5,'bright_yellow');c.restore()

 else:
  c.save();c.translate(85,55);c.rotate(t*.3)
  for radius in (18,33):
   color(c,'cyan',.8);c.set_line_width(2);c.rectangle(-radius,-radius,radius*2,radius*2);c.stroke()
  c.restore()

def cartridge(c,w,h,game,t,hot=False):
 c.scale(w/210,h/250)
 # Thick black shell, ridged grip, and a wraparound printed label.
 roundbox(c,5,4,200,237,8,'muted');roundbox(c,8,7,194,231,6,'dark_background')
 for y in range(14,53,5):
  box(c,15,y,180,2,'background')
 box(c,25,59,160,157,'foreground')
 c.save();c.rectangle(29,63,152,98);c.clip();c.translate(29,63);c.scale(152/170,98/110);illustration(c,game['id'],t);c.restore()
 box(c,29,163,152,49,game['accent'])
 text(c,game['title'],33,181,min(12,140/(len(game['title'])*.65)),'dark_background');text(c,'OMATARI / '+game.get('number','NEW'),33,201,10,'dark_background')
 box(c,57,239,96,11,'dark_background')
 for x in range(62,149,8):box(c,x,241,4,8,'yellow')
 if hot:
  color(c,game['accent'],.8);c.set_line_width(2);c.rectangle(5,4,200,235);c.stroke()

def console(c,w,h,t,selected=None,progress=0,status='INSERT A CARTRIDGE',insert=0):
 c.scale(w/560,h/360);box(c,0,0,560,360,'background')
 text(c,'OMATARI',30,36,20);text(c,'VIDEO COMPUTER SYSTEM',30,55,10,'muted')
 # Low wedge body: ribbed black top and warm woodgrain front fascia.
 roundbox(c,20,77,520,241,12,'dark_background')
 color(c,'muted');c.set_line_width(1);c.move_to(30,80);c.line_to(530,80);c.stroke()
 for x in range(33,532,7):
  box(c,x,86,2,111,'background')
  c.set_source_rgba(.6,.6,.55,.09);c.rectangle(x+2,86,1,111);c.fill()
 roundbox(c,142,94,276,43,5,'muted');roundbox(c,148,98,264,34,4,'dark_background')
 box(c,156,108,248,12,'background');box(c,160,111,240,8,'dark_background')
 accent=selected['accent'] if selected else 'orange'
 if selected:
  color(c,accent,.45+.2*math.sin(t*4));c.set_line_width(2);c.rectangle(143,95,274,41);c.stroke()
 box(c,30,202,500,67,'dark_background')
 for x,label in ((64,'POWER'),(125,'RESET')):
  roundbox(c,x-8,208,17,29,3,'background')
  box(c,x-4,213 if insert else 208,8,20,'foreground')
  box(c,x-2,214 if insert else 209,2,18,'muted')
  text(c,label,x-18,255,9)
 color(c,accent,.8);c.new_sub_path();c.arc(174,223,3,0,math.tau);c.fill()
 text(c,selected['title'] if selected else 'OMATARI',203,223,15)
 text(c,'CLICK! / POWER ON' if insert else status,203,245,10,accent)
 c.save();c.rectangle(27,272,506,36);c.clip()
 c.set_source_rgb(.32,.18,.095);c.paint()
 for i in range(24):
  y=272+i*1.6;c.set_source_rgba(.12,.055,.025,.18+(i%4)*.07);c.set_line_width(.5+(i%3)*.4)
  c.move_to(25,y)
  for x in range(25,541,8):c.line_to(x,y+math.sin(x*.027+i*1.8)*(.6+i%3*.6))
  c.stroke()
 c.restore()
 text(c,'OMATARI',43,296,16);text(c,'YOUR GAMES / ENDLESS WINDOWS',237,295,10,'bright_yellow')
 for x in (43,513):screw(c,x,315)
 text(c,'ALIGN, THEN CLICK TO INSERT',30,342,11);text(c,'R RESET / ESC CLOSE',365,342,10,'muted')

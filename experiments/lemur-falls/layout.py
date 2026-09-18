"""One authored opening composition; world positions remain player-editable."""
def arrange(app):
 x,y,w,h=app.mx,app.my,app.mw,app.mh
 app.rect=(x+60,y+100,int(app.catcher[0]+146-28-(x+60)),240)
 app.portals=[(x+w-300,y+int(h*.56),110,150),(x+w-160,y+int(h*.56),110,150)]
 # Preserve the established fixed catch and finish locations.
 app.gate=(x+30,y+h-300,w*.35,180)
 j=app.journey
 edge=app.gate[0]+app.gate[2]
 j.rects['elevator']=(edge,y+90,380,h-120)
 ex,ey,ew,eh=j.rects['elevator']
 app.apple_gate=(ex+ew,ey+10,app.goal[0]-ex-ew,180)
 for i in range(2,4):j.rects[f'plugin{i}']=(ex+325+(i-2)*90,y+h-245,56,38)

def objective(app):
 c=app.colony
 if c.saved:return 'OMACON',f'{c.saved:03} arrived / {c.lost:03} lost'
 if any(a.room==3 for a in c.lemurs):return '03 / POWER THE BAR','Drop the calendar and coffee icons into the bar slots'
 if app.barrier.health<=0:return '03 / BOARD THE LIFT','Let Tux board, then dock the calendar and coffee icons'
 if any(a.caught for a in c.lemurs):return '02 / CHAIR RIDE','Rotate the catch left; Tux will smash through Windows'
 return '01 / DIVERT THE GUNFIRE','Move a portal into the bullet stream to protect the drop'

"""Bounded, scattered popup layout around the installer."""
def layout(mx,my,mw,mh):
 home=(mx+int(mw*.34),my+int(mh*.31),int(mw*.32),int(mh*.38))
 specs=[(.025,.12,.23,.25,-.22),(.19,.035,.145,.22,.28),(.57,.045,.22,.20,-.18),(.805,.27,.175,.34,.19),(.675,.64,.29,.29,-.24),(.43,.775,.155,.19,.26),(.095,.65,.265,.29,.16),(.015,.415,.175,.22,-.29)]
 return home,{f'attack{i}':(mx+int(x*mw),my+int(y*mh),int(w*mw),int(h*mh)) for i,(x,y,w,h,a) in enumerate(specs)},{f'attack{i}':a for i,(*_,a) in enumerate(specs)}

def replacements(active,deadlines,now):
 """Keep the usual cooldown unless the desktop has no hostile windows left."""
 due=[role for role,deadline in deadlines.items() if role not in active and deadline<=now]
 if not active and deadlines and not due:
  due=[min(deadlines,key=deadlines.get)]
 return due

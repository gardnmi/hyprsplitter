"""Shared world geometry for portal rendering, routing and collision."""

def center(rect):
 x,y,w,h=rect
 return x+w*.5,y+h*.5

def core(rect):
 x,y,w,h=rect
 return x+w*.30,y+h*.22,w*.40,h*.56

def intersection(ax,ay,bx,by,rect):
 x,y,w,h=rect;low,high=0.,1.
 for start,delta,minimum,maximum in ((ax,bx-ax,x,x+w),(ay,by-ay,y,y+h)):
  if abs(delta)<1e-9:
   if not minimum<=start<=maximum:return None
  else:
   a,b=sorted(((minimum-start)/delta,(maximum-start)/delta))
   low=max(low,a);high=min(high,b)
   if low>high:return None
 return low

def beam_routes(hazard,portals,muzzle,half):
 x,y,w,h=hazard;beam=y+h*.47;start=x+muzzle;end=x+w
 hits=[]
 for i,p in enumerate(portals):
  cx,cy=center(p);_,top,_,ph=core(p)
  if start<cx<end and top<=beam<=top+ph:hits.append((cx,i))
 if len(portals)!=2 or not hits:return [(start,beam,end)],None
 stop,i=min(hits);cx,cy=center(portals[1-i]);out=cx+portals[1-i][2]*.20+10
 return [(start,beam,stop),(out,cy,max(out,end))],i

def bands(routes,half):return [(x,y-half,max(0,end-x),half*2) for x,y,end in routes if end>x]

import unittest
from model import Colony
class ColonyTests(unittest.TestCase):
 def simulate(self,ledges):
  c=Colony();c.running=True
  for _ in range(6000):c.step(.016,ledges,(450,235),680)
  return c
 def test_initial_route_saves_exactly_100(self):
  c=self.simulate([[365,340,255],[635,470,185],[830,600,230]])
  self.assertEqual((c.spawned,c.saved,c.lost),(100,100,0));self.assertFalse(c.running)
 def test_missing_catch_ledge_loses_colony(self):
  c=self.simulate([[10,340,100],[10,470,100],[830,600,230]])
  self.assertEqual(c.saved,0);self.assertEqual(c.lost,100)
 def test_source_only_walks_off_into_desktop(self):
  c=Colony();c.running=True
  for _ in range(5000):c.step(.016,[(100,380,600)],(436,335),900,exit_room=None)
  self.assertEqual((c.spawned,c.saved,c.lost),(100,0,100))
 def test_pause_freezes_release(self):
  c=Colony();c.step(1,[]);self.assertEqual(c.spawned,0)
 def test_long_drop_is_fatal(self):
  c=self.simulate([[350,570,400],[830,600,230]])
  self.assertEqual(c.lost,100)
class HazardTests(unittest.TestCase):
 def test_all_100_intercepted(self):
  c=Colony();c.running=True
  for _ in range(5000):
   c.step(.016,[(100,400,600)],(160,355),1100,exit_room=None,hazard=(0,800,2048,18))
  self.assertEqual((c.spawned,c.shot,c.lost),(100,100,100))
 def test_fast_fall_cannot_tunnel_through_bullets(self):
  from model import Lemur
  c=Colony();c.running=True;c.spawned=100;c.lemurs=[Lemur(400,400,70,vy=4000,drop=400)]
  c.step(.2,[],bottom=1200,exit_room=None,hazard=(0,600,2000,18))
  self.assertEqual(c.shot,1);self.assertLessEqual(c.lemurs[0].y,618)
  c.step(.2,[],bottom=1200,exit_room=None,hazard=(0,600,2000,18))
  self.assertEqual(c.shot,1)
class EffectTests(unittest.TestCase):
 def test_final_splat_expires_even_when_colony_stops(self):
  c=Colony();c.splats=[(100,200,0.)];c.running=False
  c.step(.5,[]);self.assertEqual(len(c.splats),1)
  c.step(.5,[]);self.assertEqual(c.splats,[])
  self.assertEqual(c.spawned,0)
class PortalTests(unittest.TestCase):
 def test_bullets_are_cut_off_and_redirected(self):
  from portals import beam_routes
  routes,index=beam_routes((0,600,1800,82),[(400,560,100,150),(900,200,100,150)],90,3.6)
  self.assertEqual(index,0);self.assertEqual(routes[0][2],450)
  self.assertEqual(routes[1],(980,275,1800))
 def test_either_portal_can_intercept(self):
  from portals import beam_routes
  _,i=beam_routes((0,600,1800,82),[(900,200,100,150),(400,560,100,150)],90,3.6)
  self.assertEqual(i,1)
 def test_falling_lemur_teleports_and_does_not_loop(self):
  from model import Lemur
  c=Colony();c.spawned=100;c.running=True
  a=Lemur(450,315,70,vy=100);c.lemurs=[a]
  p=[(400,280,100,150),(900,200,100,150)]
  c.step(.1,[],bottom=1200,exit_room=None,portals=p)
  self.assertEqual(a.teleports,1);self.assertGreater(a.x,970);self.assertEqual(c.lost,0)
  c.step(.01,[],bottom=1200,exit_room=None,portals=p);self.assertEqual(a.teleports,1)
 def test_portal_cannot_rescue_after_earlier_bullet_hit(self):
  from model import Lemur
  c=Colony();c.spawned=100;c.running=True;c.lemurs=[Lemur(450,200,70,vy=1000)]
  c.step(.2,[],bottom=1200,exit_room=None,hazards=[(0,230,2000,8)],portals=[(400,280,100,150),(900,200,100,150)])
  self.assertEqual(c.shot,1);self.assertEqual(c.lemurs[0].teleports,0)
 def test_portal_blocks_original_firing_lane(self):
  from portals import beam_routes,bands
  routes,_=beam_routes((0,800,2048,82),[(400,765,110,150),(1100,200,110,150)],90,3.6)
  c=Colony();c.running=True
  for _ in range(5000):c.step(.016,[(100,400,600)],(160,355),1100,exit_room=None,hazards=bands(routes,3.6))
  self.assertEqual(c.shot,0)
class CatcherTests(unittest.TestCase):
 def test_catcher_softens_drop_and_releases_left(self):
  from model import Lemur
  c=Colony();c.running=True;c.spawned=100;a=Lemur(850,100,70,drop=100);c.lemurs=[a]
  for _ in range(400):
   c.step(.016,[(800,600,199)],bottom=1200,exit_room=None,left_rooms=(0,),soft_rooms=(0,))
   if a.room==0:break
  self.assertEqual(a.state,'walk');self.assertLess(a.speed,0);self.assertEqual(c.lost,0)
  for _ in range(300):
   c.step(.016,[(800,600,199)],bottom=1200,exit_room=None,left_rooms=(0,),soft_rooms=(0,))
   if a.room is None:break
  self.assertIsNone(a.room);self.assertLess(a.x,800)
class RotatingCatcherTests(unittest.TestCase):
 def test_upright_holds_and_tilt_releases_to_left(self):
  import math
  from model import Lemur
  c=Colony();c.running=True;c.spawned=100;a=Lemur(145,0,70);c.lemurs=[a]
  for _ in range(600):c.step(1/120,[],bottom=900,exit_room=None,catcher=((0,0,230,210),0,0))
  self.assertEqual(c.lost,0);self.assertTrue(a.caught)
  self.assertGreater(a.x,30);self.assertLess(a.x,200);self.assertLess(a.y,210)
  previous=0
  for i in range(1800):
   angle=-math.radians(120)*min(1,i/120)
   c.step(1/120,[],bottom=900,exit_room=None,catcher=((0,0,230,210),angle,previous));previous=angle
   if a.x<0:break
  self.assertLess(a.x,0);self.assertLess(a.speed,0)
 def test_closed_floor_stops_fast_fall(self):
  from model import Lemur
  from catcher import resolve
  a=Lemur(100,210,70,vy=2200)
  resolve(a,100,120,.05,(0,0,230,210),0,0)
  self.assertLess(a.y,180);self.assertTrue(a.caught)

class DestinationTests(unittest.TestCase):
 def run_fall(self,hazard=None):
  from model import Lemur
  c=Colony();c.running=True;c.spawned=100;c.lemurs=[Lemur(100,0,0,vy=2000)]
  c.step(.2,[],bottom=900,exit_room=None,goal=(0,150,200,100),hazard=hazard)
  return c
 def test_fast_arrival_rescues_once(self):
  c=self.run_fall();self.assertEqual(c.saved,1);self.assertEqual(c.lost,0)
  c.step(.2,[],goal=(0,150,200,100));self.assertEqual(c.saved,1)
 def test_gunfire_before_goal_is_lethal(self):
  c=self.run_fall((0,50,200,8));self.assertEqual(c.saved,0);self.assertEqual(c.shot,1)
 def test_goal_before_gunfire_is_safe(self):
  c=self.run_fall((0,300,200,8));self.assertEqual(c.saved,1);self.assertEqual(c.shot,0)

class BarrierTests(unittest.TestCase):
 def test_beam_stops_until_all_panes_break(self):
  from barrier import Barrier
  b=Barrier();window=(0,0,400,180);r=[(0,110,900)]
  self.assertEqual(b.step(.1,r,window),[(0,110,296)])
  health=b.health;b.step(.5,[(0,10,900)],window);self.assertEqual(b.health,health)
  for _ in range(40):b.step(.1,r,window)
  self.assertEqual(b.health,0);self.assertEqual(b.step(.1,r,window),r)
 def test_walkers_wait_then_pass(self):
  from model import Lemur
  c=Colony();c.spawned=100;c.running=True;a=Lemur(130,160,70,room=0,state='walk');c.lemurs=[a]
  for _ in range(60):c.step(.016,[(0,160,400)],exit_room=None,blockers=[(160,70,80,90)])
  self.assertEqual(a.x,152)
  for _ in range(60):c.step(.016,[(0,160,400)],exit_room=None)
  self.assertGreater(a.x,160)
 def test_walkers_are_not_immune_to_redirected_fire(self):
  from model import Lemur
  c=Colony();c.spawned=100;c.running=True;c.lemurs=[Lemur(130,160,70,room=0,state='walk')]
  c.step(.016,[(0,160,400)],exit_room=None,hazards=[(0,145,400,8)])
  self.assertEqual(c.shot,1)

class JourneyTests(unittest.TestCase):
 def setup_route(self):
  from types import SimpleNamespace
  from mechanics import Journey
  from layout import arrange
  app=SimpleNamespace(mx=0,my=0,mw=2048,mh=1152,goal=(1616,60,400,210),catcher=(327,508,230,210))
  app.journey=Journey(0,0,2048,1152,app.goal);arrange(app)
  return app
 def test_only_icons_and_lift_remain(self):
  app=self.setup_route();self.assertEqual(set(app.journey.roles),{'plugin2','plugin3','elevator'})
  self.assertEqual(set(app.journey.rects),set(app.journey.roles))
 def test_direct_boarding_and_ride_to_omacon(self):
  from model import Lemur
  app=self.setup_route();j=app.journey;c=Colony();c.spawned=100;c.running=True
  gx,gy,gw,gh=app.gate;ax,ay,aw,ah=app.apple_gate;floor=gy+gh-20
  self.assertAlmostEqual(gx+gw,j.lift()[0]);self.assertAlmostEqual(floor,j.lift()[1])
  a=Lemur(gx+10,floor,80,room=1,state='walk');c.lemurs=[a]
  def step():
   j.step(.01,c)
   c.step(.01,[(-10000,-10000,0),(gx,floor,gw),(ax,ay+ah-20,aw)]+j.ledges(),bottom=1152,exit_room=None,goal=app.goal,soft_rooms=(1,2,3),waiting_rooms=(3,) if j.progress<.999 else ())
  for _ in range(1600):step()
  self.assertEqual(a.room,3);self.assertEqual(c.lost,0)
  for i,(sx,sy) in enumerate(j.sockets()):j.rects[f'plugin{i+2}']=(sx-28,sy-19,56,38)
  for _ in range(1800):step()
  self.assertEqual(c.saved,1);self.assertEqual(c.lost,0)

class SingleLemurTests(unittest.TestCase):
 def test_only_one_spawns_and_death_ends_run(self):
  c=Colony(total=1);c.running=True
  for _ in range(500):c.step(.02,[],source=(100,10),bottom=500,exit_room=None)
  self.assertEqual(c.spawned,1);self.assertEqual(len(c.lemurs),1);self.assertEqual(c.lost,1);self.assertFalse(c.running)
 def test_arrival_stops_run_but_effect_clock_continues(self):
  c=Colony(total=1);c.running=True
  for _ in range(100):c.step(.02,[],source=(100,10),bottom=500,goal=(0,100,400,200),exit_room=None)
  self.assertEqual(c.saved,1);self.assertFalse(c.running)
  before=c.effect_time;c.step(.2,[]);self.assertGreater(c.effect_time,before)

class WindowsDepartureTests(unittest.TestCase):
 def test_blue_screen_only_after_live_exit(self):
  from barrier import Barrier
  from model import Lemur
  b=Barrier();a=Lemur(100,100,70,room=1,state='walk')
  b.observe_exit([1],[a]);self.assertIsNone(b.departed_at)
  a.room=None;a.state='lost';b.observe_exit([1],[a]);self.assertIsNone(b.departed_at)
  a.room=3;a.state='walk';b.time=12;b.observe_exit([1],[a]);self.assertEqual(b.departed_at,12)
  b.time=14;b.observe_exit([1],[a]);self.assertEqual(b.departed_at,12)
  self.assertIsNone(Barrier().departed_at)

class AppleSurpriseTests(unittest.TestCase):
 def test_slide_hits_ball_once_then_exit_triggers_message(self):
  from barrier import Barrier
  from model import Lemur
  b=Barrier();a=Lemur(154,160,70,room=2,state='walk');r=(0,0,400,180)
  b.observe_apple([2],[130],[a],r);self.assertEqual(b.ball_hit_at,0)
  b.time=1;b.observe_apple([2],[130],[a],r);self.assertEqual(b.ball_hit_at,0);self.assertIsNone(b.departed_at)
  a.room=None;a.state='saved';b.observe_apple([2],[154],[a],r);self.assertEqual(b.departed_at,1)
 def test_death_does_not_trigger_apple_celebration(self):
  from barrier import Barrier
  from model import Lemur
  b=Barrier();a=Lemur(154,160,70,state='lost')
  b.observe_apple([2],[130],[a],(0,0,400,180));self.assertIsNone(b.departed_at);self.assertIsNone(b.ball_hit_at)

class ChairTerrainTests(unittest.TestCase):
 def test_lands_on_hill_then_rides_to_adjacent_lift(self):
  from model import Lemur
  from terrain import ground
  rect=(0,100,700,180);ledges=[(-1000,0,1),(0,260,700),(2000,260,100),(700,260,300)]
  colony=Colony(total=1);colony.spawned=1;colony.running=True
  a=Lemur(280,120,75,drop=120);colony.lemurs=[a]
  for _ in range(100):
   colony.step(.016,ledges,exit_room=None,soft_rooms=(1,),windows_terrain=rect)
   if a.room==1:break
  self.assertEqual(a.room,1);self.assertAlmostEqual(a.y,ground(a.x,rect),places=4)
  for _ in range(800):
   colony.step(.016,ledges,exit_room=None,windows_terrain=rect)
   if a.room==3:break
   self.assertAlmostEqual(a.y,ground(a.x,rect),places=4)
  self.assertEqual(a.room,3);self.assertEqual(colony.lost,0)

class ChairCrashTests(unittest.TestCase):
 def test_crash_breaks_logo_ejects_tux_and_lands_on_lift(self):
  from barrier import Barrier
  from model import Lemur
  b=Barrier();rect=(0,100,700,180);lift=(700,260,380)
  a=Lemur(588,260,75,room=1,state='walk')
  b.time=2
  self.assertTrue(b.chair_impact([a],rect,lift))
  self.assertEqual(b.health,0);self.assertEqual(b.departed_at,2)
  self.assertEqual(a.state,'fall');self.assertLess(a.vy,0)
  self.assertFalse(b.chair_impact([a],rect,lift));self.assertEqual(len(b.bursts),1)
  colony=Colony(total=1);colony.spawned=1;colony.running=True;colony.lemurs=[a]
  ledges=[(-1000,0,1),(0,260,700),(2000,260,100),lift]
  for _ in range(90):
   colony.step(.016,ledges,exit_room=None,soft_rooms=(1,3),windows_terrain=rect)
   if a.room is not None:break
  self.assertEqual(a.room,3);self.assertEqual(colony.lost,0)
 def test_does_not_break_before_contact(self):
  from barrier import Barrier
  from model import Lemur
  b=Barrier();a=Lemur(500,260,75,room=1,state='walk')
  self.assertFalse(b.chair_impact([a],(0,100,700,180),(700,260,380)))
  self.assertEqual(b.health,1)

if __name__=='__main__':unittest.main()

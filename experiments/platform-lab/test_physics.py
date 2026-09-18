import unittest
from physics import Walker,neighbor

class Platforms(unittest.TestCase):
 def test_gap_causes_fall_and_death(self):
  g={'start':(0,0,220,160),'goal':(880,0,220,160)}
  w=Walker();w.running=True
  for _ in range(200):w.step(.03,g,bottom=500)
  self.assertTrue(w.dead);self.assertIsNone(w.room);self.assertFalse(w.won)
 def test_connected_bridge_is_safe(self):
  g={'start':(0,0,220,160),'bridge':(230,0,640,160),'goal':(880,0,220,160)}
  w=Walker();w.running=True
  for _ in range(500):w.step(.03,g)
  self.assertTrue(w.won);self.assertFalse(w.dead)
 def test_fall_lands_on_lower_platform(self):
  g={'start':(0,0,220,160),'bridge':(220,160,400,160)}
  w=Walker();w.running=True
  for _ in range(200):
   w.step(.02,g)
   if w.room=='bridge':break
  self.assertEqual(w.room,'bridge');self.assertFalse(w.falling);self.assertIn('bridge',w.visited)
 def test_lift_carries_local_position(self):
  g={'start':(0,0,220,160),'bridge':(240,0,620,160),'goal':(880,-185,220,160)}
  w=Walker();w.running=True
  while w.room=='start':w.step(.03,g)
  x=w.x;g['bridge']=(240,-185,620,160)
  self.assertEqual(w.x,x)
  for _ in range(400):w.step(.03,g)
  self.assertTrue(w.won)
 def test_locked_door_waits_instead_of_falling(self):
  g={'start':(0,0,220,160),'goal':(230,0,220,160)}
  w=Walker();w.running=True
  for _ in range(200):w.step(.03,g,False)
  self.assertTrue(w.waiting);self.assertFalse(w.falling)
 def test_sweep_catches_narrow_platform_between_frame_endpoints(self):
  w=Walker();w.running=True;w.falling=True;w.room=None
  w.world_x=0;w.world_y=0;w.vy=1000
  w.step(.1,{'bridge':(3, -110, 3, 200)})
  self.assertEqual(w.room,'bridge');self.assertFalse(w.falling)
 def test_sweep_chooses_first_surface_crossed(self):
  w=Walker();w.running=True;w.falling=True;w.room=None;w.vy=1000
  w.step(.1,{'bridge':(0,-110,100,200),'goal':(0,-70,100,200)})
  self.assertEqual(w.room,'bridge')
 def test_pausing_freezes_fall(self):
  w=Walker();w.running=True;w.falling=True;w.world_y=100
  w.step(.1,{},bottom=500);y=w.world_y;w.running=False;w.step(.5,{})
  self.assertEqual(w.world_y,y)


class SurfaceTests(unittest.TestCase):
 def test_speed_changes_by_material(self):
  g={'start':(0,0,2000,400)}
  distances=[]
  for kind in ('mud','flat','fast'):
   w=Walker();w.running=True;w.step(1,g,surfaces={'start':kind});distances.append(w.x-38)
  self.assertAlmostEqual(distances[0],90*.42)
  self.assertAlmostEqual(distances[1],90)
  self.assertAlmostEqual(distances[2],90*1.8)
 def test_hill_profile_and_handoff(self):
  from experiments.surfaces import height,slope
  self.assertEqual(height(500,500,0,'hill'),height(500,500,500,'hill'))
  self.assertLess(height(500,500,250,'hill'),height(500,500,0,'hill'))
  self.assertLess(slope(500,500,125,'hill'),0)
  self.assertGreater(slope(500,500,375,'hill'),0)
  g={'start':(0,0,200,500),'bridge':(210,0,500,500),'goal':(720,0,200,500)}
  w=Walker();w.running=True
  for _ in range(700):w.step(.03,g,surfaces={'bridge':'hill'})
  self.assertTrue(w.won);self.assertFalse(w.dead)
 def test_falling_lands_on_hill_surface(self):
  g={'bridge':(0,100,500,500)}
  w=Walker();w.running=True;w.falling=True;w.room=None;w.world_x=180;w.world_y=350
  for _ in range(50):
   w.step(.02,g,surfaces={'bridge':'hill'})
   if not w.falling:break
  self.assertFalse(w.falling);self.assertEqual(w.room,'bridge')

if __name__=='__main__':unittest.main()

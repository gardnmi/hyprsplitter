import unittest
from model import Jump

G={'ramp':(0,0,420,360),'sky':(420,-65,520,450),'landing':(940,0,420,360)}

class Flight(unittest.TestCase):
 def flight(self,power,g=None):
  j=Jump();j.state='charging';j.charge=power;j.release()
  for _ in range(900):
   j.step(1/120,g or G)
   if j.state in ('landed','missed'):return j
  return j
 def test_middle_charge_lands_through_sky(self):
  j=self.flight(.7);self.assertEqual(j.state,'landed');self.assertTrue(j.sun)
 def test_short_and_long_jumps_miss(self):
  for p in (.1,1.):self.assertEqual(self.flight(p).state,'missed')
 def test_moving_landing_changes_result(self):
  g=dict(G);g['landing']=(2000,0,420,360)
  self.assertEqual(self.flight(.7,g).state,'missed')
 def test_charge_caps_and_release_only_once(self):
  j=Jump();j.state='charging';j.step(3,G);self.assertEqual(j.charge,1)
  j.release();j.step(.1,G);x=j.local;j.release();self.assertEqual(j.local,x)

class LandingRamp(unittest.TestCase):
 def test_touchdown_and_rollout_follow_slope(self):
  from model import landing_y
  j=Flight().flight(.78);lx,ly,w,h=G['landing']
  self.assertAlmostEqual(j.y,ly+landing_y(w,h,j.local))
  self.assertLess(j.y,ly+h-42)
  for _ in range(40):
   j.step(.01,G)
   self.assertAlmostEqual(j.y,ly+landing_y(w,h,j.local))
 def test_swept_collision_catches_ramp_before_flat_floor(self):
  from model import landing_hit,landing_y
  r=(0,0,420,360);hit=landing_hit(100,200,200,310,r)
  self.assertIsNotNone(hit)
  self.assertAlmostEqual(hit[1],landing_y(420,360,hit[0]))
  self.assertLess(hit[1],318)
 def test_does_not_catch_car_already_under_ramp(self):
  from model import landing_hit
  self.assertIsNone(landing_hit(50,310,80,330,(0,0,420,360)))

class AdjustableRamp(unittest.TestCase):
 def test_launch_follows_selected_slope(self):
  import math
  from model import ramp_y
  for rise in (35,90,150):
   j=Jump(rise);j.state='charging';j.charge=.7;j.release()
   while j.state=='runup':j.step(.005,G)
   self.assertAlmostEqual(-j.vy/j.vx,rise/(420*.5))
   self.assertAlmostEqual(j.y,ramp_y(420,360,420*.88,rise))
 def test_steeper_ramp_launches_higher(self):
  from model import ramp_y
  self.assertLess(ramp_y(420,360,370,150),ramp_y(420,360,370,35))

class Secrets(unittest.TestCase):
 def test_panel_pass_triggers_fireworks_once(self):
  j=Flight().flight(.7);self.assertTrue(j.fireworks)
  age=j.firework_age;j.step(.02,G);self.assertGreater(j.firework_age,age)
 def test_off_center_pass_also_triggers_fireworks(self):
  j=Flight().flight(.78);self.assertTrue(j.sun);self.assertTrue(j.fireworks)
 def test_missing_panel_does_not_trigger(self):
  g=dict(G);g['sky']=(420,-1000,520,450)
  self.assertFalse(Flight().flight(.78,g).fireworks)
 def test_crossing_between_frames_counts(self):
  from model import crosses_panel
  self.assertTrue(crosses_panel(-20,50,120,50,(0,0,100,100)))
  self.assertFalse(crosses_panel(-20,150,120,150,(0,0,100,100)))
 def test_reset_clears_fireworks(self):
  j=Jump();self.assertFalse(j.fireworks);self.assertEqual(j.firework_age,0)

class Rewards(unittest.TestCase):
 def test_sky_window_is_not_enough_for_bonus(self):
  g=dict(G);g['sky']=(420,-160,520,450)
  j=Flight().flight(.7,g);self.assertEqual(j.state,'landed');self.assertFalse(j.sun)
 def test_accuracy_rewards_and_score_freezes(self):
  j=Flight().flight(.78);self.assertTrue(j.perfect);self.assertGreater(j.score,3000)
  score=j.score
  for _ in range(100):j.step(.01,G)
  self.assertEqual(j.score,score)
 def test_failed_attempt_has_no_completion_score(self):
  self.assertEqual(Flight().flight(1).score,0)
 def test_swept_target_detection(self):
  from model import segment_distance
  self.assertEqual(segment_distance(-100,0,100,0,0,0),0)
 def test_passport_persists_best_and_requires_all_challenges(self):
  import tempfile
  from pathlib import Path
  from progress import Passport
  with tempfile.TemporaryDirectory() as d:
   path=Path(d)/'passport.json';p=Passport(path)
   p.record(3200,1,True);p.record(2000,2,False)
   self.assertFalse(Passport(path).game['stamp'])
   p.record(2500,2,True);p.record(2800,3,True)
   loaded=Passport(path);self.assertTrue(loaded.game['stamp']);self.assertEqual(loaded.game['best'],3200)

if __name__=='__main__':unittest.main()

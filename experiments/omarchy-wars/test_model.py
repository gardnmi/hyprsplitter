import unittest
from model import Game,Enemy,Shot,W,H
class CombatTests(unittest.TestCase):
 def play(self):
  g=Game(1);g.state='play';g.spawn=999;return g
 def test_intro_reaches_combat(self):
  g=Game(1);g.state='install'
  for _ in range(1050):g.step(.016)
  self.assertEqual(g.state,'play');self.assertEqual(g.hp,3)
 def test_fast_bullet_sweeps_through_target(self):
  g=self.play();g.enemies=[Enemy(580,360,0,age=1)];g.shots=[Shot(550,360,1000,0)]
  g.step(.04);self.assertEqual(g.score,100);self.assertFalse(g.enemies)
 def test_dash_protects_against_collision(self):
  g=self.play();g.enemies=[Enemy(g.x,g.y,0,age=1)]
  g.step(.016,dash=True);self.assertEqual(g.hp,3);self.assertGreater(g.dash_cool,0)
 def test_invulnerability_prevents_multi_hit_death(self):
  g=self.play();g.enemies=[Enemy(g.x,g.y,0,age=1) for _ in range(5)]
  g.step(.016);self.assertEqual(g.hp,2)
  g.damage();self.assertEqual(g.hp,2)
 def test_death_stops_combat(self):
  g=self.play();g.hp=1;g.damage();self.assertEqual(g.state,'over')
  x=g.x;g.step(.04,move=(1,0),shoot=True);self.assertEqual(g.x,x);self.assertFalse(g.shots)
 def test_movement_stays_inside_arena(self):
  g=self.play()
  for _ in range(200):g.step(.04,move=(1,-1))
  self.assertLessEqual(g.x,W-30);self.assertGreaterEqual(g.y,95)
 def test_effects_and_projectiles_expire(self):
  g=self.play();g.burst(0,0,'red');g.shots=[Shot(1099,360,1000,0)]
  for _ in range(30):g.step(.04)
  self.assertFalse(g.shots);self.assertFalse(g.sparks)

class WindowInteractionTests(unittest.TestCase):
 def board(self,gap=6):
  from board import Board
  return Board({'home':(100,100,250,250),'breach':(350+gap,100,180,180),'scanner':(750,100,180,180),'repair':(100,450,200,150)})
 def test_joined_window_receives_ship(self):
  b=self.board();x,y=b.constrain(349,170,363,170)
  self.assertEqual(b.room(x,y),'breach')
 def test_gap_blocks_ship_and_fast_bullet(self):
  b=self.board(60);x,y=b.constrain(349,170,425,170)
  self.assertEqual(b.room(x,y),'home')
  self.assertIsNone(b.projectile(330,170,445,170))
 def test_bullet_crosses_joined_windows(self):
  b=self.board();result=b.projectile(330,170,405,170)
  self.assertIsNotNone(result);self.assertEqual(b.room(*result),'breach')
 def test_drag_carries_ship_and_enemy(self):
  b=self.board();g=Game(1,board=b);g.enemies=[Enemy(400,170,0)]
  old=g.x;new=dict(b.rects);new['home']=(150,100,250,250);new['breach']=(406,100,180,180)
  b.relocate(new,g);self.assertEqual(g.x,old+50);self.assertEqual(g.enemies[0].x,450)
 def test_isolated_attackers_cannot_escape_room(self):
  b=self.board(60);g=Game(1,board=b);g.state='play';g.spawn=999;g.enemies=[Enemy(430,170,0,age=1)]
  for _ in range(100):g.step(.016)
  self.assertEqual(b.room(g.enemies[0].x,g.enemies[0].y),'breach');self.assertEqual(g.hp,3)


class PopupInvasionTests(unittest.TestCase):
 def test_shots_cross_empty_desktop(self):
  from board import Board
  b=Board({'home':(100,100,200,200),'attack0':(700,100,200,200)},invasion=True)
  self.assertEqual(b.projectile(250,200,750,200),(750,200))
  self.assertLess(b.constrain(250,200,500,200)[0],300)
 def test_remote_invader_can_be_destroyed(self):
  from board import Board
  b=Board({'home':(100,100,200,200),'attack0':(700,100,200,200)},invasion=True)
  g=Game(1,board=b);g.state='play';g.spawn=99999
  g.enemies=[Enemy(750,200,0,age=1)];g.shots=[Shot(310,200,850,0)]
  for _ in range(40):g.step(.016)
  self.assertEqual(g.score,100);self.assertFalse(g.enemies)
 def test_popup_layout_stays_on_monitor_and_varies(self):
  from invasion import layout
  for mw,mh in ((1920,1080),(1366,768)):
   home,rects,tilts=layout(0,0,mw,mh)
   self.assertEqual(len(rects),8);self.assertGreater(len({r[2:] for r in rects.values()}),3)
   for x,y,w,h in rects.values():self.assertTrue(0<=x<x+w<=mw and 0<=y<y+h<=mh)


class SmallHitboxTests(unittest.TestCase):
 def test_bullet_misses_outside_smaller_enemy(self):
  g=Game(1);g.state='play';g.spawn=99999
  g.enemies=[Enemy(600,360,0,age=1)];g.shots=[Shot(570,375,1000,0)]
  g.step(.04);self.assertEqual(g.score,0);self.assertEqual(len(g.enemies),1)

class MobileInvaderTests(unittest.TestCase):
 def game(self):
  from board import Board
  b=Board({'home':(100,100,220,220),'attack0':(700,100,220,200)},invasion=True)
  g=Game(2,board=b);g.state='play';g.spawn=99999;g.invuln=999
  return g
 def test_invader_leaves_window_and_enters_install(self):
  g=self.game();e=Enemy(760,200,0,age=1);e.room='attack0';g.enemies=[e]
  for _ in range(450):g.step(.04)
  self.assertEqual(g.board.room(e.x,e.y),'home');self.assertIsNone(e.room)
 def test_window_has_independent_health_and_delayed_replacement(self):
  g=self.game();g.nodes['attack0']={'hp':2,'max':2,'cool':999}
  escaped=Enemy(500,300,0,age=1);g.enemies=[escaped]
  for _ in range(2):
   g.shots=[Shot(715,200,850,0)];g.step(.04)
  self.assertEqual(g.nodes['attack0']['hp'],0);self.assertEqual(g.destroyed,1)
  self.assertIn(escaped,g.enemies);self.assertEqual(g.score,1000)
  delay=g.respawns['attack0']-g.playtime
  self.assertGreaterEqual(delay,4.99);self.assertLessEqual(delay,10)
  deadline=g.respawns['attack0'];g.shots=[Shot(715,200,850,0)];g.step(.04)
  self.assertEqual(g.destroyed,1);self.assertEqual(g.respawns['attack0'],deadline)
 def test_live_node_reinforces_but_dead_node_does_not(self):
  g=self.game();g.nodes['attack0']={'hp':14,'max':14,'cool':0}
  g.step(.04);self.assertEqual(len(g.enemies),1)
  g.nodes['attack0'].update(hp=0,cool=0);g.step(.04);self.assertEqual(len(g.enemies),1)


class DifficultyAndPhaseTests(unittest.TestCase):
 def test_opening_and_ramp(self):
  from difficulty import settings
  early=settings(2);late=settings(150)
  self.assertEqual(early['rooms'],2);self.assertEqual(early['ships'],1)
  self.assertFalse(early['can_shoot']);self.assertEqual(late['rooms'],8)
  self.assertGreater(late['speed'],early['speed']);self.assertGreater(late['cap'],early['cap'])
  self.assertLess(late['fire_interval'],early['fire_interval'])
 def test_no_early_gunfire_and_phasing_between_windows(self):
  from board import Board
  b=Board({'home':(100,100,220,220),'attack0':(700,100,220,200)},invasion=True)
  g=Game(1,board=b);g.state='play';g.spawn=99999;g.invuln=999
  e=Enemy(500,200,1,age=1,cool=0);g.enemies=[e]
  g.step(.04);self.assertTrue(e.phasing);self.assertFalse(g.shots)
  e.x,e.y=200,200;g.step(.04);self.assertFalse(e.phasing)
  g.playtime=25;e.x=500;e.cool=0;g.step(.04);self.assertTrue(any(b.enemy for b in g.shots))

class EmptyDesktopTests(unittest.TestCase):
 def test_last_window_replaced_immediately(self):
  from invasion import replacements
  self.assertEqual(replacements(set(),{'attack0':30,'attack1':24},10),['attack1'])
 def test_other_windows_preserve_normal_delay(self):
  from invasion import replacements
  self.assertEqual(replacements({'attack1'},{'attack0':30},10),[])
  self.assertEqual(replacements({'attack1'},{'attack0':30},30),['attack0'])
 def test_no_enemies_required_to_fire(self):
  g=Game(1);g.state='play';g.spawn=99999
  g.step(.016,aim=(900,360),shoot=True)
  self.assertEqual(len(g.shots),1);self.assertFalse(g.shots[0].enemy)
 def test_click_on_empty_overlay_fires_instead_of_dragging(self):
  from main import App,Gdk
  from types import SimpleNamespace
  from unittest.mock import Mock
  app=App.__new__(App);app.game=Game(1);app.game.state='play';app.windows={};app.shooting=False
  area=Mock();area.get_allocated_width.return_value=1100;area.get_allocated_height.return_value=720
  app.button(area,SimpleNamespace(button=1,type=Gdk.EventType.BUTTON_PRESS,x=750,y=5),'air')
  self.assertTrue(app.shooting);self.assertEqual(app.aim,(750,5))
  app.button(area,SimpleNamespace(button=1,type=Gdk.EventType.BUTTON_RELEASE,x=750,y=5),'air')
  self.assertFalse(app.shooting)


class PowerupTests(unittest.TestCase):
 def game(self):
  g=Game(7);g.state='play';g.spawn=999;return g
 def test_collect_upgrades_and_caps(self):
  from model import Pickup
  g=self.game()
  for expected in (2,3,4,4):
   g.pickups=[Pickup(g.x,g.y,0,0)]
   g.step(.001)
   self.assertEqual(g.lasers,expected)
  self.assertFalse(g.pickups)
 def test_volley_count_and_symmetry(self):
  for level in range(1,5):
   g=self.game();g.lasers=level
   g.step(.001,aim=(g.x+100,g.y),shoot=True)
   self.assertEqual(len(g.shots),level)
   self.assertAlmostEqual(sum(b.y for b in g.shots)/level,g.y)
 def test_spawn_expiry_and_reset(self):
  g=self.game();g.pickup_due=0;g.step(.01)
  self.assertEqual(len(g.pickups),1)
  g.pickups[0].life=.001;g.step(.01)
  self.assertFalse(g.pickups)
  self.assertEqual(Game().lasers,1)
 def test_warning_holds(self):
  g=Game();g.state='warning'
  for _ in range(100):g.step(.04)
  self.assertEqual(g.state,'warning')
  for _ in range(15):g.step(.04)
  self.assertEqual(g.state,'play')


class FasterWavesTests(unittest.TestCase):
 def test_grouped_waves_reach_eight_by_36_seconds(self):
  from difficulty import settings
  self.assertEqual([settings(t)['rooms'] for t in (0,11,12,24,36)],[2,2,4,6,8])
  self.assertEqual(settings(12)['ships'],2)
  self.assertEqual(settings(30)['ships'],3)
 def test_late_respawns_keep_pressure(self):
  from difficulty import settings
  early,late=settings(0),settings(60)
  self.assertLess(late['respawn_high'],early['respawn_low'])
  self.assertGreater(late['node_hp'],early['node_hp'])
  self.assertTrue(settings(12)['can_shoot'])


class CrossWindowInputTests(unittest.TestCase):
 def test_internal_focus_transfer_preserves_held_fire_and_keys(self):
  from main import App
  app=App.__new__(App);app.title='Omatari-ZeroDay-123';app.keys={'w'};app.shooting=True
  for role in ('air','attack0','home'):
   app.update_input_focus(app.title+'-'+role)
   self.assertTrue(app.shooting);self.assertEqual(app.keys,{'w'})
  app.update_input_focus('other-app')
  self.assertFalse(app.shooting);self.assertFalse(app.keys)
 def test_first_click_on_enemy_window_fires_even_near_top_edge(self):
  from main import App,Gdk
  from board import Board
  from types import SimpleNamespace
  from unittest.mock import Mock
  app=App.__new__(App);app.game=Game(1);app.game.state='play';app.shooting=False
  app.board=Board({'attack0':(700,100,200,200)},invasion=True)
  area=Mock();area.get_allocated_width.return_value=200;area.get_allocated_height.return_value=200
  app.button(area,SimpleNamespace(button=1,type=Gdk.EventType.BUTTON_PRESS,x=100,y=5),'attack0')
  self.assertTrue(app.shooting)
  app.game.spawn=999
  app.game.step(.016,aim=app.aim,shoot=app.shooting)
  self.assertEqual(len(app.game.shots),1)
  app.button(area,SimpleNamespace(button=1,type=Gdk.EventType.BUTTON_RELEASE,x=100,y=5),'attack0')
  self.assertFalse(app.shooting)

if __name__=='__main__':unittest.main()

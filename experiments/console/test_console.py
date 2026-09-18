import unittest
from unittest.mock import Mock,patch
from catalog import aligned,GAMES

class SlotTests(unittest.TestCase):
 def test_contacts_fit_slot(self):
  self.assertTrue(aligned((100,300,560,360),(275,165,210,250)))
 def test_nearby_body_is_not_contacts(self):
  self.assertFalse(aligned((100,300,560,360),(275,310,210,250)))
  self.assertFalse(aligned((100,300,560,360),(510,165,210,250)))
 def test_scaled_and_offset_monitor(self):
  self.assertTrue(aligned((2000,300,280,180),(2087.5,232.6,105,125)))
 def test_all_cartridges_point_to_existing_games(self):
  from pathlib import Path
  self.assertEqual(len({g['id'] for g in GAMES}),len(GAMES))
  for g in GAMES:self.assertTrue(Path(g['command'][1]).is_file())

class LaunchTests(unittest.TestCase):
 def test_game_launch_and_failure_restore_cartridge(self):
  from main import Launcher
  import tempfile
  import os
  for fails in (False,True):
   with self.subTest(fails=fails),tempfile.TemporaryDirectory() as directory,patch.dict(os.environ,{'XDG_CACHE_HOME':directory}),patch('main.subprocess.Popen') as spawn:
    app=Launcher.__new__(Launcher);app.windows={'quattro':Mock()};app.child=None;app.inserting=(GAMES[1],10.)
    if fails:spawn.side_effect=OSError('test failure')
    app.launch(GAMES[1])
    spawn.assert_called_once();self.assertEqual(spawn.call_args.args[0],GAMES[1]['command'])
    app.windows['quattro'].set_opacity.assert_called_with(1)
    if fails:self.assertTrue(app.reset_pending);self.assertIn('FAILED',app.status);self.assertIsNone(app.inserting)
    else:
     self.assertEqual(app.inserting,(GAMES[1],10.))
     app.log.close()


class LifecycleTests(unittest.TestCase):
 def make_app(self):
  from main import Launcher
  app=Launcher.__new__(Launcher)
  app.closed=False;app.child=None;app.hypr=Mock();app.workspace=4;app.prefix='test';app.placed=True;app.reset_pending=False
  app.windows={r:Mock() for r in ['console']+[g['id'] for g in GAMES]}
  app.starts={'console':(100,300,560,360),'space':(0,0,210,250),'quattro':(275,165,210,250),'tux':(900,0,210,250)}
  for i,g in enumerate(GAMES):app.starts.setdefault(g['id'],(1200+i*250,0,210,250))
  app.armed=None;app.candidate=None;app.last_rect=None;app.inserting=None;app.since=0;app.position=Mock();app.launch=Mock()
  clients=[dict(initialTitle='test-'+r,at=list(rect[:2]),size=list(rect[2:]),workspace={'id':4}) for r,rect in app.starts.items()]
  app.hypr.request.side_effect=lambda cmd,parse: {'id':4} if cmd=='activeworkspace' else clients
  return app
 def test_one_insertion_then_launch(self):
  app=self.make_app()
  with patch('main.time.monotonic',return_value=10):app.sync()
  self.assertEqual(app.candidate,'quattro');self.assertIsNone(app.inserting)
  with patch('main.time.monotonic',return_value=10.7):app.sync()
  self.assertEqual(app.armed,'quattro');self.assertIsNone(app.inserting)
  app.launch.assert_not_called()
  with patch('main.time.monotonic',return_value=10.8):
   app.drag(Mock(),Mock(button=1),app.windows['quattro'])
  with patch('main.time.monotonic',return_value=11.8):app.sync()
  app.launch.assert_called_once_with(GAMES[1])
 def test_exit_restores_all_cartridges(self):
  app=self.make_app();app.child=Mock();app.child.poll.return_value=0;app.log=Mock()
  app.sync()
  self.assertIsNone(app.child);self.assertEqual(app.status,'WELCOME BACK')
  self.assertEqual(app.position.call_count,len(GAMES)+1)
  for win in app.windows.values():win.set_opacity.assert_called_with(1)

class InsertionMotionTests(unittest.TestCase):
 def test_press_rebounds_and_seats(self):
  from insertion import travel,seat_rect
  self.assertEqual(travel(0),0)
  self.assertGreater(travel(.12),travel(.24))
  self.assertEqual(travel(1),170)
  self.assertEqual(seat_rect((100,300,560,360),(0,0,210,250)),(275,165,210,250))

class PowerSafetyTests(unittest.TestCase):
 def test_power_click_does_not_close_launcher(self):
  from main import Launcher
  from types import SimpleNamespace
  app=Launcher.__new__(Launcher);app.inserting=None;app.armed=None;app.close=Mock()
  win=Mock();app.windows={'console':win};area=Mock()
  area.get_allocation.return_value=SimpleNamespace(width=560,height=360)
  app.drag(area,SimpleNamespace(button=1,x=65,y=220),win)
  app.close.assert_not_called();win.begin_move_drag.assert_not_called()

if __name__=='__main__':unittest.main()

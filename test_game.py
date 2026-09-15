import unittest
from game import Game, side
from field import COLUMNS, ROWS, SECTORS, DODGES, WARNING, MAX_ROCKS, grid_steps
from controls import MISSIONS, shortcut_labels

ARENA = (0, 0, 1200, 900)
def rect(x=0,y=0,w=600,h=900,floating=False,mode=0):
    return {'at':[x,y], 'size':[w,h], 'floating':floating, 'fullscreen':mode}

class Lessons(unittest.TestCase):
    def game(self, mission):
        g = Game(mission, seed=12)
        g.controls = shortcut_labels([])
        g.observe({4:rect()}, ARENA, 4)
        g.start()
        return g

    def test_every_lesson_starts_with_a_briefing(self):
        for mission in MISSIONS:
            g = Game(mission[0])
            g.advance(100)
            self.assertEqual(g.state,'briefing')
            self.assertFalse(g.rocks)

    def test_lessons_reset_all_other_mechanics(self):
        g = self.game('asteroids');g.spawn_rocks()
        for mission in MISSIONS[1:]:
            g.load(mission[0]);g.start();g.advance(1)
            self.assertFalse(g.rocks)
            self.assertFalse(g.pending)
            self.assertEqual(bool(g.enemies), mission[0]=='shoot')

    def test_asteroids_require_both_travel_and_dodges(self):
        g = self.game('asteroids');g.progress=DODGES
        g.advance(.1);self.assertEqual(g.state,'active')
        for y in range(ROWS):
            for x in range(COLUMNS):
                g.observe({4:rect(x*1200/COLUMNS,y*900/ROWS,1200/COLUMNS,900/ROWS)},ARENA,4)
        g.advance(.1);self.assertEqual(g.state,'complete')
        self.assertFalse(g.rocks)

    def test_asteroid_hit_does_not_count_as_a_dodge(self):
        g = self.game('asteroids');g.rocks={g.ship_slot:.1}
        g.advance(.2)
        self.assertEqual(g.progress,0)
        self.assertIn('HIT',g.feedback)
        self.assertEqual(g.state,'active')

    def test_each_random_arrival_gets_a_full_warning(self):
        g = self.game('asteroids');g.pending=[(.1,1),(.8,2)]
        g.advance(.2);self.assertEqual(g.rocks,{1:WARNING})
        g.advance(.7);self.assertEqual(g.rocks[2],WARNING)
        self.assertLess(g.rocks[1],WARNING)

    def test_random_bursts_include_solos_clusters_and_staggered_arrivals(self):
        g=self.game('asteroids');sizes=set();simultaneous=False;staggered=False
        for _ in range(100):
            g.pending=[];g.spawn_rocks();sizes.add(len(g.pending))
            self.assertIn(g.ship_slot,[s for _,s in g.pending])
            if len(g.pending)>1:
                simultaneous |= len({d for d,_ in g.pending})==1
                staggered |= len({d for d,_ in g.pending})>1
        self.assertIn(1,sizes);self.assertTrue(simultaneous and staggered)

    def test_large_grid_and_overlapping_asteroids_leave_clear_sectors(self):
        steps = grid_steps()
        self.assertEqual(len(steps), SECTORS)
        created = set()
        for actor, parent, _, _ in steps:
            self.assertTrue(parent is None or parent in created)
            self.assertNotIn(actor, created)
            created.add(actor)
        self.assertEqual(created, set(range(SECTORS)))
        g=self.game('asteroids')
        peak=0
        for _ in range(1000):
            g.advance(.05)
            threatened=set(g.rocks) | {s for _,s in g.pending}
            peak=max(peak,len(threatened))
            self.assertLessEqual(len(threatened),MAX_ROCKS)
            self.assertTrue(all(0 <= s < SECTORS for s in threatened))
        self.assertGreaterEqual(peak,6)

    def test_pause_and_floating_cannot_advance_asteroid_lesson(self):
        g=self.game('asteroids');g.rocks={0:2};g.paused=True;g.advance(5)
        self.assertEqual(g.rocks[0],2)
        g.paused=False;g.observe({4:rect(floating=True)},ARENA,4);g.advance(5)
        self.assertEqual(g.rocks[0],2)
        self.assertIn('RETURN TO TILING',g.instruction())

    def test_laser_wrong_side_retries_same_gate(self):
        g=self.game('lasers');g.advance(5.1)
        self.assertEqual(g.progress,0);self.assertIn('TRY',g.feedback)
        self.assertEqual(g.safe_side,'top')

    def test_laser_rotation_then_swap_hints_and_all_four_gates(self):
        g=self.game('lasers')
        self.assertIn('ROTATE',g.instruction())
        g.observe({4:rect(0,450,1200,450)},ARENA,4)
        self.assertIn('SWAP TO TOP',g.instruction())
        for r in (rect(0,0,1200,450),rect(600,0),rect(0,450,1200,450),rect()):
            g.cooldown=0;g.observe({4:r},ARENA,4)
            self.assertIn('SAFE',g.instruction());g.advance(5.1)
        self.assertEqual(g.state,'complete')

    def test_focus_does_not_shoot_and_friendly_is_not_a_target(self):
        g=self.game('shoot');g.observe({4:rect(),0:rect(600,0)},ARENA,0)
        g.advance(100)
        self.assertEqual(len(g.enemies),3)
        self.assertIn('DESTROY',g.instruction())
        self.assertFalse(g.close_target(4))
        for actor in (0,1,2):
            self.assertTrue(g.close_target(actor))
            self.assertFalse(g.close_target(actor))
        self.assertEqual(g.state,'complete')

    def test_closes_do_not_award_progress_in_briefing_or_pause(self):
        g=Game('shoot');self.assertFalse(g.close_target(0))
        g.start();g.paused=True;self.assertFalse(g.close_target(0))

    def test_docking_requires_float_movement_to_beacon_and_landing(self):
        g=self.game('float')
        g.observe({4:rect(floating=True)},ARENA,4);self.assertEqual(g.step,1)
        g.observe({4:rect()},ARENA,4);self.assertEqual(g.state,'active')
        self.assertEqual(g.step,0)
        g.observe({4:rect(floating=True)},ARENA,4)
        g.observe({4:rect(700,300,400,300,True)},ARENA,4);self.assertEqual(g.step,2)
        g.observe({4:rect()},ARENA,4);self.assertEqual(g.state,'complete')

    def test_resize_requires_width_then_restoration_and_rejects_fullscreen(self):
        g=self.game('resize')
        g.observe({4:rect(w=1200,mode=2)},ARENA,4);g.advance(1);self.assertEqual(g.step,0)
        g.observe({4:rect(w=740)},ARENA,4);g.advance(.7);self.assertEqual(g.step,1)
        g.observe({4:rect(w=600)},ARENA,4);g.advance(.7);self.assertEqual(g.state,'complete')

    def test_fullscreen_and_maximize_are_distinct_and_require_return(self):
        for name,mode in [('fullscreen',2),('maximize',1)]:
            g=self.game(name)
            g.observe({4:rect(mode=3-mode)},ARENA,4);self.assertEqual(g.step,0)
            self.assertIn('EXIT THIS MODE',g.instruction())
            g.observe({4:rect(mode=mode)},ARENA,4);self.assertEqual(g.step,1)
            self.assertEqual(g.state,'active')
            g.observe({4:rect()},ARENA,4);self.assertEqual(g.state,'complete')

    def test_fullscreen_labels_follow_installed_custom_bindings(self):
        labels=shortcut_labels([{'description':'Full screen','modmask':72,'key':'F'},
                                {'description':'Full width','modmask':64,'key':'F'}])
        self.assertEqual(labels['fullscreen'],'Super+Alt+F')
        self.assertEqual(labels['maximize'],'Super+F')

    def test_two_window_side_classification(self):
        self.assertEqual(side(rect(),ARENA),'left')
        self.assertEqual(side(rect(600,0),ARENA),'right')
        self.assertEqual(side(rect(0,0,1200,450),ARENA),'top')
        self.assertEqual(side(rect(0,450,1200,450),ARENA),'bottom')
        self.assertIsNone(side(rect(100,100,200,200),ARENA))

if __name__=='__main__':
    unittest.main()

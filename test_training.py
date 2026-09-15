import unittest

from controls import shortcut_labels
from game import Game


class TrainingTests(unittest.TestCase):
    def test_default_opening_is_one_slow_lane_without_enemies(self):
        game = Game(1)
        game.start()
        self.assertTrue(game.training)
        self.assertEqual(game.kind, "laser")
        self.assertEqual(len(game.hazards), 3)
        self.assertEqual(game.duration, 3.2)
        self.assertFalse(game.enemies)
        self.assertEqual(game.boss, 0)

    def test_each_new_mechanic_waits_for_acknowledgement(self):
        game = Game(1)
        game.start()
        for wave, lesson in ((4, "asteroids"), (7, "shoot"), (10, "float"),
                             (13, "grow"), (16, "split"), (19, "fullscreen"), (22, "boss")):
            game.wave = wave-1
            game.next_wave()
            self.assertEqual((game.phase, game.lesson), ("briefing", lesson))
            self.assertFalse(game.hazards)
            state = (game.wave, game.shields, game.remaining, game.energy)
            game.advance(100)
            self.assertEqual(state, (game.wave, game.shields, game.remaining, game.energy))
            game.start()
            self.assertEqual(game.wave, wave)
            self.assertEqual(game.phase, "aim" if lesson == "shoot" else "warning")
        self.assertEqual(game.boss, 1)

    def test_first_asteroid_lesson_has_only_three_warned_rocks(self):
        game = Game(2)
        game.wave = 3
        game.next_wave()
        game.start()
        self.assertEqual(game.kind, "asteroid")
        self.assertEqual(len(game.asteroid_timers) + len(game.asteroid_pending), 3)
        self.assertGreaterEqual(min(game.asteroid_timers.values()), 2.8)
        self.assertFalse(game.enemies)

    def test_shooting_practice_waits_for_a_kill_without_incoming_hazards(self):
        game = Game(2)
        game.wave = 6
        game.next_wave()
        game.start()
        self.assertEqual(game.enemies, {0: 3})
        game.advance(100)
        self.assertEqual((game.phase, game.shields, game.wave), ("aim", 3, 7))
        self.assertFalse(game.hazards)
        game.damage(0, 3)
        game.advance(.1)
        self.assertEqual(game.phase, "cooldown")
        game.advance(game.remaining)
        self.assertEqual((game.phase, game.wave, game.enemies), ("aim", 8, {2: 3}))

    def test_boss_and_enemies_do_not_appear_before_their_lessons(self):
        game = Game(3)
        for wave in range(1, 22):
            game.next_wave()
            if game.phase == "briefing":
                game.start()
            self.assertEqual(game.wave, wave)
            self.assertEqual(game.boss, 0)
            if wave < 7:
                self.assertFalse(game.enemies)
            else:
                self.assertTrue(game.enemies)

    def test_fullscreen_labels_follow_installed_custom_bindings(self):
        labels = shortcut_labels([
            {"description": "Full screen", "key": "F", "modmask": 72, "submap": ""},
            {"description": "Full width", "key": "F", "modmask": 64, "submap": ""},
            {"description": "Full screen", "key": "Q", "modmask": 64, "submap": "unrelated"},
        ])
        self.assertEqual(labels["fullscreen"], "Super+Alt+F")
        self.assertEqual(labels["maximize"], "Super+F")

    def test_normal_clock_reaches_all_briefings_before_boss(self):
        game = Game(4)
        game.start()
        briefings = []
        for _ in range(5000):
            if game.phase == "briefing":
                briefings.append(game.lesson)
                game.start()
            if game.boss:
                break
            if game.phase == "aim":
                for enemy in list(game.enemies):
                    game.damage(enemy, 3)
            safe = set(range(9)) - game.hazards
            if safe:
                game.ship = min(safe)
            game.advance(.1)
        self.assertEqual(briefings, ["asteroids", "shoot", "float", "grow", "split", "fullscreen", "boss"])
        self.assertEqual((game.wave, game.shields, game.boss), (22, 3, 1))


if __name__ == "__main__":
    unittest.main()

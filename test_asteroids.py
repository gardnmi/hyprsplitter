from collections import Counter
import unittest

from game import Game


class AsteroidTests(unittest.TestCase):
    def wave(self, seed=12):
        game = Game(seed, training=False)
        game.wave = 2
        game.next_wave()
        return game

    def test_random_showers_include_singles_and_simultaneous_groups(self):
        schedules = set()
        for seed in range(30):
            game = self.wave(seed)
            self.assertTrue(game.asteroid_pending)
            impacts = list(game.asteroid_timers.values()) + [delay+warning for delay, warning in game.asteroid_pending.values()]
            sizes = Counter(impacts).values()
            self.assertEqual(len(impacts), 6)
            self.assertIn(1, sizes)
            self.assertTrue(any(size >= 2 for size in sizes))
            self.assertTrue(all(warning >= game.duration for _, warning in game.asteroid_pending.values()))
            schedules.add(tuple(round(value, 3) for value in sorted(impacts)))
        self.assertGreater(len(schedules), 20)

    def test_future_rocks_are_hidden_until_they_appear_and_wave_waits(self):
        game = self.wave()
        game.ship = 8
        game.asteroid_timers = {0: .2}
        game.asteroid_pending = {1: (1.0, .5), 2: (1.0, .5)}
        game.asteroid_delays = {0: .2}
        game.hazards = {0}
        game.advance(.2)
        self.assertEqual(game.phase, 'warning')
        self.assertFalse(game.hazards)
        self.assertFalse(game.asteroid_timers)
        self.assertEqual(len(game.asteroid_pending), 2)
        game.advance(.8)
        self.assertEqual(game.hazards, {1, 2})
        self.assertAlmostEqual(game.asteroid_timers[1], .5)
        self.assertAlmostEqual(game.asteroid_timers[2], .5)
        game.advance(.5)
        self.assertEqual(set(game.asteroid_flashes), {1, 2})
        self.assertEqual(game.phase, 'impact')

    def test_cluster_collision_uses_position_at_impact(self):
        game = self.wave()
        game.asteroid_pending = {}
        game.asteroid_timers = {0: .5, 1: .5, 2: 1.2}
        game.hazards = {0, 1, 2}
        game.ship = 0
        game.advance(.5)
        self.assertEqual(game.shields, 2)
        self.assertEqual(set(game.asteroid_flashes), {0, 1})
        self.assertEqual(game.hazards, {2})
        game.advance(.7)
        self.assertEqual(game.shields, 2)  # Cleared sector remains safe.
        self.assertEqual(game.phase, 'impact')

    def test_pause_freezes_pending_arrivals_and_active_countdowns(self):
        game = self.wave()
        pending, timers = game.asteroid_pending.copy(), game.asteroid_timers.copy()
        game.paused = True
        game.advance(10)
        self.assertEqual(game.asteroid_pending, pending)
        self.assertEqual(game.asteroid_timers, timers)
        game.restart()
        self.assertFalse(game.asteroid_pending)
        self.assertFalse(game.asteroid_timers)

    def test_wave_finishes_after_all_arrivals_and_impacts(self):
        game = self.wave()
        all_targets = set(game.asteroid_timers) | set(game.asteroid_pending)
        game.ship = min(set(range(9))-all_targets)
        for _ in range(200):
            game.advance(.05)
            if game.phase == 'impact':
                break
        self.assertFalse(game.asteroid_pending)
        self.assertFalse(game.asteroid_timers)
        self.assertEqual(game.score, 120)
        self.assertEqual(game.shields, 3)
        game.advance(game.remaining)
        game.advance(game.remaining)
        self.assertEqual(game.kind, 'laser')


if __name__ == '__main__':
    unittest.main()

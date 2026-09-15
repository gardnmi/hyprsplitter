import unittest

from game import Game


class AsteroidTests(unittest.TestCase):
    def setUp(self):
        self.game = Game(12)
        self.game.wave = 2
        self.game.next_wave()

    def test_each_asteroid_has_a_distinct_randomized_deadline(self):
        timers = sorted(self.game.asteroid_timers.values())
        self.assertEqual(len(timers), 6)
        self.assertAlmostEqual(timers[0], self.game.duration)
        for earlier, later in zip(timers, timers[1:]):
            self.assertGreaterEqual(later-earlier, .18)
            self.assertLessEqual(later-earlier, .34)

    def test_first_impact_does_not_detonate_other_tiles(self):
        game = self.game
        first = min(game.asteroid_timers, key=game.asteroid_timers.get)
        game.ship = first
        game.advance(game.asteroid_timers[first])
        self.assertEqual(game.shields, 2)
        self.assertEqual(game.phase, "warning")
        self.assertEqual(set(game.asteroid_flashes), {first})
        self.assertEqual(len(game.asteroid_timers), 5)
        self.assertNotIn(first, game.hazards)
        game.advance(min(game.asteroid_timers.values()))
        self.assertEqual(game.shields, 2)  # The cleared tile stays safe.
        self.assertEqual(len(game.asteroid_timers), 4)

    def test_collision_uses_position_at_each_individual_impact(self):
        game = self.game
        first = min(game.asteroid_timers, key=game.asteroid_timers.get)
        game.ship = next(i for i in range(9) if i not in game.hazards)
        game.advance(game.asteroid_timers[first])
        self.assertEqual(game.shields, 3)
        second = min(game.asteroid_timers, key=game.asteroid_timers.get)
        game.ship = second
        game.advance(game.asteroid_timers[second])
        self.assertEqual(game.shields, 2)
        self.assertEqual(game.asteroid_hits, {second})

    def test_wave_finishes_after_last_asteroid_and_pause_freezes_timers(self):
        game = self.game
        game.ship = next(i for i in range(9) if i not in game.hazards)
        snapshot = game.asteroid_timers.copy()
        game.paused = True
        game.advance(10)
        self.assertEqual(game.asteroid_timers, snapshot)
        game.paused = False
        while game.asteroid_timers:
            game.advance(min(game.asteroid_timers.values()))
        self.assertEqual(game.phase, "impact")
        self.assertEqual(game.score, 120)
        self.assertEqual(game.shields, 3)
        self.assertFalse(game.hazards)
        game.advance(game.remaining)
        game.advance(game.remaining)
        self.assertEqual(game.kind, "laser")
        self.assertFalse(game.asteroid_timers)
        self.assertFalse(game.asteroid_flashes)


if __name__ == "__main__":
    unittest.main()

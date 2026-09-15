import unittest

from game import Game


class GameTests(unittest.TestCase):
    def test_edges_do_not_wrap(self):
        game = Game(1)
        game.ship = 0
        self.assertIsNone(game.neighbor("left"))
        self.assertIsNone(game.neighbor("up"))
        self.assertEqual(game.neighbor("right"), 1)
        self.assertEqual(game.neighbor("down"), 3)

    def test_warning_is_safe_and_impact_damages_only_once(self):
        game = Game(1)
        game.start()
        game.ship = next(iter(game.hazards))
        game.advance(game.remaining / 2)
        self.assertEqual(game.shields, 3)
        game.advance(game.remaining)
        self.assertEqual(game.shields, 2)
        game.advance(.1)
        self.assertEqual(game.shields, 2)

    def test_dodge_scores_and_pause_freezes_time(self):
        game = Game(2)
        game.start()
        game.ship = next(i for i in range(9) if i not in game.hazards)
        game.paused = True
        before = game.remaining
        game.advance(20)
        self.assertEqual(game.remaining, before)
        game.paused = False
        game.advance(before)
        self.assertEqual(game.score, 100)
        self.assertEqual(game.shields, 3)

    def test_three_hits_end_game_and_restart_resets(self):
        game = Game(3)
        game.start()
        for _ in range(3):
            if game.kind == "asteroid":
                game.next_wave()  # Exercise shield depletion with synchronized lasers.
            game.ship = next(iter(game.hazards))
            game.advance(game.remaining)
            game.advance(game.remaining)
            if game.phase != "over":
                game.advance(game.remaining)
        self.assertEqual(game.phase, "over")
        game.restart()
        self.assertEqual((game.phase, game.shields, game.score), ("ready", 3, 0))

    def test_hard_waves_force_a_dodge_but_leave_reachable_safe_tiles(self):
        game = Game(4)
        for _ in range(100):
            game.next_wave()
            self.assertEqual(len(game.hazards), 6)
            self.assertIn(game.ship, game.hazards)
            self.assertGreaterEqual(game.duration, .65)
            self.assertLessEqual(game.duration, .95)
            row, col = divmod(game.ship, 3)
            safe = set(range(9)) - game.hazards
            self.assertLessEqual(min(abs(row - i//3) + abs(col - i%3) for i in safe), 2)
            game.ship = game.rng.choice(sorted(safe))

    def test_opening_wave_is_hard_after_restart(self):
        game = Game(5)
        for _ in range(2):
            game.start()
            self.assertEqual(game.duration, .95)
            self.assertEqual(len(game.hazards), 6)
            game.advance(game.remaining)
            self.assertEqual(game.remaining, .25)
            game.advance(game.remaining)
            self.assertEqual(game.remaining, .12)
            game.restart()


if __name__ == "__main__":
    unittest.main()

import unittest

from combat import firing_lane, neighbor, aim_guidance, overlaps
from game import Game


def rect(x, y, w=100, h=100, floating=False):
    return {"at": [x, y], "size": [w, h], "floating": floating}


class CombatTests(unittest.TestCase):
    def setUp(self):
        self.game = Game(7, training=False)
        self.game.start()

    def test_bullets_hit_first_aligned_enemy_and_stop(self):
        geometry = {4: rect(110, 220), 1: rect(110, 110), 0: rect(110, 0), 2: rect(0, 0)}
        target, path = firing_lane(geometry, 4, {1, 0, 2}, "up")
        self.assertEqual((target, path), (1, [4, 1]))
        self.assertEqual(firing_lane(geometry, 4, {0, 2}, "up"), (0, [4, 1, 0]))
        self.assertIsNone(firing_lane(geometry, 4, {0}, "down")[0])

    def test_aim_guidance_explains_how_to_line_up(self):
        geometry = {4: rect(110, 220), 0: rect(0, 0)}
        self.assertEqual(aim_guidance(geometry, 4, {0}), (None, "MOVE LEFT TO LINE UP"))
        geometry[0] = rect(220, 0)
        self.assertEqual(aim_guidance(geometry, 4, {0}), (None, "MOVE RIGHT TO LINE UP"))
        geometry[0] = rect(110, 330)
        self.assertEqual(aim_guidance(geometry, 4, {0}), (None, "MOVE BELOW THE RED TARGET"))
        geometry[0] = rect(110, 0)
        self.assertEqual(aim_guidance(geometry, 4, {0}), (0, "TARGET LOCKED / AUTO-FIRING UP"))

    def test_physical_navigation_handles_unequal_tiles_and_blockers(self):
        geometry = {4: rect(110, 220), 1: rect(0, 110, 320), 0: rect(110, 0), 9: rect(110, 160, floating=True)}
        self.assertEqual(neighbor(geometry, 4, "up"), 1)
        self.assertIsNone(neighbor(geometry, 4, "up", {1}))

    def test_fire_cooldown_and_growth_damage(self):
        game = self.game
        self.assertTrue(game.fire("up", [0], [4, 1, 0]))
        self.assertEqual(game.enemies[0], 2)
        self.assertFalse(game.fire("up", [0], [4, 0]))
        game.advance(.33)
        game.ability("grow")
        self.assertTrue(game.fire("up", [0], [4, 0]))
        self.assertNotIn(0, game.enemies)
        self.assertEqual(game.score, 250)

    def test_energy_cost_and_ability_duration(self):
        game = self.game
        self.assertTrue(game.ability("float"))
        self.assertEqual(game.energy, 65)
        self.assertEqual(game.flight, 3)
        game.advance(1)
        self.assertEqual(game.flight, 2)
        game.energy = 0
        self.assertFalse(game.ability("grow"))
        self.assertEqual(game.growth, 0)
        self.assertTrue(game.ability("float"))  # Landing is always free.

    def test_enemy_contact_costs_one_shield_and_cannot_spam_damage(self):
        game = self.game
        self.assertTrue(game.ram(0))
        self.assertEqual(game.shields, 2)
        self.assertEqual(game.enemies[0], 3)
        self.assertFalse(game.ram(0))
        self.assertEqual(game.shields, 2)
        self.assertGreater(game.contact_flash, 0)

    def test_destroying_enemy_repairs_shield_and_clears_contact_danger(self):
        game = self.game
        game.ram(0)
        game.damage(0, 3)
        self.assertEqual(game.shields, 3)
        self.assertEqual(game.score, 250)
        self.assertIn("SHIELD +1", game.reward_text)
        self.assertNotIn(0, game.enemies)
        game.contact_cooldown = 0
        self.assertFalse(game.ram(0))
        game.damage(2, 3)
        self.assertEqual(game.shields, 3)
        self.assertIn("SHIELDS FULL", game.reward_text)

    def test_contact_cannot_hurt_during_briefing_and_can_end_run(self):
        game = self.game
        game.phase = "briefing"
        self.assertFalse(game.ram(0))
        game.phase = "aim"
        game.shields = 1
        self.assertTrue(game.ram(0))
        self.assertEqual((game.shields, game.phase), (0, "over"))

    def test_only_overlapping_rectangles_make_floating_contact(self):
        self.assertFalse(overlaps(rect(0, 0), rect(100, 0)))
        self.assertFalse(overlaps(rect(0, 0), rect(110, 110)))
        self.assertTrue(overlaps(rect(0, 0), rect(90, 40, floating=True)))

    def test_wing_is_vulnerable_while_primary_floats(self):
        game = self.game
        game.ability("split")
        game.ability("float")
        game.wing = next(iter(game.hazards))
        game.advance(game.remaining)
        self.assertEqual(game.shields, 2)

    def test_boss_progression_and_nova_do_not_skip_new_phase(self):
        game = self.game
        game.wave = 4
        game.next_wave()
        self.assertEqual((game.boss, game.enemies), (1, {0: 18}))
        game.damage(0, 10)
        game.ability("fullscreen")
        self.assertEqual(game.boss, 2)
        self.assertEqual(game.enemies, {0: 6, 10: 6, 11: 6})
        for index in (0, 10, 11):
            game.damage(index, 6)
        self.assertEqual((game.boss, game.enemies), (3, {0: 12}))
        game.damage(0, 12)
        self.assertEqual(game.phase, "victory")
        game.advance(2)
        self.assertEqual(game.burst, 0)

    def test_pause_freezes_abilities_and_restart_clears_them(self):
        game = self.game
        game.ability("split")
        game.ability("grow")
        game.paused = True
        game.advance(20)
        self.assertEqual(game.growth, 5)
        self.assertFalse(game.fire("up", [0], [0]))
        game.restart()
        self.assertFalse(game.split)
        self.assertEqual((game.boss, game.growth, game.flight, game.burst, game.energy), (0, 0, 0, 0, 100))


if __name__ == "__main__":
    unittest.main()

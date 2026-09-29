import unittest

from model import Game, HEIGHT, WIDTH, SHAPES


class GameTests(unittest.TestCase):
    def test_bags_contain_all_seven_pieces(self):
        game = Game(7)
        kinds = []
        for _ in range(21):
            kinds.append(game.kind)
            game.spawn()
        for start in (0, 7, 14):
            self.assertEqual(set(kinds[start:start + 7]), set(SHAPES))

    def test_seed_reproduces_sequence(self):
        a, b = Game(71), Game(71)
        self.assertEqual((a.kind, a.queue), (b.kind, b.queue))

    def test_walls_floor_and_occupied_cells_block_motion(self):
        game = Game(1)
        game.spawn('O')
        while game.move(-1):
            pass
        self.assertEqual(min(x for x, y in game.cells()), 0)
        self.assertFalse(game.move(-1))
        game.board[2][0] = 'Z'
        self.assertFalse(game.move(0, 1))
        game.board[2][0] = None
        while game.move(0, 1):
            pass
        self.assertEqual(max(y for x, y in game.cells()), HEIGHT - 1)

    def test_four_rotations_restore_shape(self):
        game = Game(2)
        for kind in SHAPES:
            game.spawn(kind)
            original = set(game.cells())
            for _ in range(4):
                game.rotate()
            self.assertEqual(set(game.cells()), original)

    def test_rotation_kicks_off_floor(self):
        game = Game(2)
        game.spawn('T')
        game.y = 18
        self.assertTrue(game.rotate())
        self.assertTrue(all(0 <= y < HEIGHT for x, y in game.cells()))

    def test_blocked_rotation_does_not_change_piece(self):
        game = Game(2)
        game.spawn('T')
        game.y = 8
        cells = set(game.cells())
        game.board = [[None if (x, y) in cells else 'J' for x in range(WIDTH)]
                      for y in range(HEIGHT)]
        self.assertFalse(game.rotate())
        self.assertEqual(set(game.cells()), cells)

    def test_ghost_and_hard_drop_agree(self):
        game = Game(3)
        landing = game.cells(game.ghost_y())
        kind = game.kind
        distance = game.ghost_y() - game.y
        game.hard_drop()
        self.assertTrue(all(game.board[y][x] == kind for x, y in landing))
        self.assertEqual(game.score, distance * 2)

    def test_four_lines_clear_and_rows_collapse(self):
        game = Game(3)
        game.spawn('I')
        game.rotate()
        game.x, game.y = 2, 16
        for y in range(16, HEIGHT):
            game.board[y] = ['J'] * WIDTH
            game.board[y][4] = None
        game.board[15][0] = 'O'
        game.hard_drop()
        self.assertEqual(game.lines, 4)
        self.assertEqual(game.score, 800)
        self.assertEqual(game.board[19][0], 'O')
        self.assertTrue(all(cell is None for row in game.board[:19] for cell in row))

    def test_hold_only_once_per_piece_and_swap_resets_position(self):
        game = Game(4)
        first, second = game.kind, game.queue[0]
        game.hold()
        self.assertEqual((game.held, game.kind), (first, second))
        game.hold()
        self.assertEqual((game.held, game.kind), (first, second))
        game.hard_drop()
        third = game.kind
        game.move(-1)
        game.rotate()
        game.hold()
        self.assertEqual((game.kind, game.held), (first, third))
        self.assertEqual((game.x, game.y, game.shape), (3, 0, SHAPES[first]))

    def test_lock_delay_and_reset_limit(self):
        game = Game(5)
        game.spawn('O')
        game.y = 18
        for _ in range(4):
            game.update(.1)
        self.assertFalse(any(any(row) for row in game.board))
        for i in range(16):
            game.move(1 if i % 2 == 0 else -1)
        self.assertEqual(game.lock_resets, 15)
        for _ in range(6):
            game.update(.1)
        self.assertEqual(sum(bool(cell) for row in game.board for cell in row), 4)

    def test_soft_drop_scores_and_long_delays_are_clamped(self):
        game = Game(1)
        game.update(10., True)
        self.assertEqual(game.y, 2)
        self.assertEqual(game.score, 2)

    def test_blocked_spawn_ends_game_and_input_stops(self):
        game = Game(1)
        game.board[0] = ['Z'] * WIDTH
        game.board[1] = ['Z'] * WIDTH
        game.spawn('O')
        before = [row[:] for row in game.board]
        self.assertTrue(game.over)
        self.assertFalse(game.move(1))
        self.assertFalse(game.rotate())
        game.hold()
        game.hard_drop()
        game.update(.1)
        self.assertEqual(game.board, before)

    def test_level_increases_speed(self):
        game = Game(1)
        initial = game.interval
        game.lines = 10
        self.assertEqual(game.level, 2)
        self.assertLess(game.interval, initial)


if __name__ == '__main__':
    unittest.main()

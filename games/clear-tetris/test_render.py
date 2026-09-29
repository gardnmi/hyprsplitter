"""Verify that the board actually preserves the video beneath empty cells."""
import unittest

import cairo

from model import Game
from render import draw, WINDOW_W, WINDOW_H, BOARD_X, BOARD_Y, CELL


class TransparencyTests(unittest.TestCase):
    def pixel(self, surface, x, y):
        surface.flush()
        offset = y * surface.get_stride() + x * 4
        return bytes(surface.get_data()[offset:offset + 4])

    def test_empty_cells_are_clear_and_blocks_are_visible(self):
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WINDOW_W, WINDOW_H)
        c = cairo.Context(surface)
        c.set_source_rgb(1, 0, 0)
        c.paint()
        game = Game(1)
        game.board[10][5] = 'I'
        draw(c, game, paused=False)
        self.assertEqual(self.pixel(surface, BOARD_X + 13, BOARD_Y + 10 * CELL + 13), b'\0' * 4)
        self.assertNotEqual(self.pixel(surface, BOARD_X + 5 * CELL + 13, BOARD_Y + 10 * CELL + 13), b'\0' * 4)

    def test_optional_tint_adds_backdrop(self):
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WINDOW_W, WINDOW_H)
        draw(cairo.Context(surface), Game(1), paused=False, tint=.28)
        self.assertNotEqual(self.pixel(surface, BOARD_X + 13, BOARD_Y + 10 * CELL + 13), b'\0' * 4)

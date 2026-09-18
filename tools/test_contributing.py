import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'experiments/console'))
from catalog import load_games, starting_layout
from new_game import create_game


class ContributionTests(unittest.TestCase):
    def fixture(self, directory):
        root = Path(directory)
        (root/'experiments/console').mkdir(parents=True)
        (root/'experiments/console/games.json').write_text('[]')
        (root/'templates/window-game').mkdir(parents=True)
        (root/'templates/window-game/main.py').write_text('raise RuntimeError("discovery must not execute games")')
        return root

    def test_scaffold_is_discovered_without_executing_it(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.fixture(directory)
            created = create_game('my-game', 'MY GAME', root)
            games = load_games(root)
            self.assertEqual(games[0]['id'], 'my-game')
            self.assertEqual(Path(games[0]['command'][1]), created/'main.py')
            with self.assertRaises(ValueError):
                create_game('my-game', 'NO OVERWRITE', root)

    def test_invalid_slug_does_not_create_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.fixture(directory)
            for slug in ('../escape','console','CAPITAL','with space'):
                with self.assertRaises(ValueError):
                    create_game(slug, 'TEST', root)
            self.assertFalse((root/'games').exists())

    def test_invalid_manifest_reports_path(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.fixture(directory)
            created = create_game('bad', 'BAD', root)
            path = created/'game.json'
            data = json.loads(path.read_text())
            data['entry'] = '/tmp/not-a-game.py'
            path.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, 'game.json'):
                load_games(root)

    def test_extra_cartridges_stay_on_scaled_offset_monitor(self):
        for count in (4,5,8,12):
            games = [{'id':f'game-{i}'} for i in range(count)]
            rects, _ = starting_layout((1920,40,1280,720),games)
            for x,y,w,h in rects.values():
                self.assertGreaterEqual(x,1920)
                self.assertGreaterEqual(y,40)
                self.assertLessEqual(x+w,3200)
                self.assertLessEqual(y+h,760)

    def test_new_cartridge_art_has_no_builtin_id_requirement(self):
        import cairo
        from art import cartridge
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,210,250)
        cartridge(cairo.Context(surface),210,250,
                  {'id':'community','title':'COMMUNITY','accent':'cyan','number':'05'},0)


if __name__ == '__main__':
    unittest.main()

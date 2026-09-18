import unittest
from model import docked


class DockingTests(unittest.TestCase):
    def test_full_containment_wins(self):
        self.assertTrue(docked((120,120,60,60), (100,100,200,200)))

    def test_partial_overlap_does_not_win(self):
        self.assertFalse(docked((90,120,60,60), (100,100,200,200)))

    def test_separate_windows_do_not_win(self):
        self.assertFalse(docked((500,500,60,60), (100,100,200,200)))


if __name__ == '__main__':
    unittest.main()

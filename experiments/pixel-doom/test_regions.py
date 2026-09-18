"""Check native-pixel coverage without opening any windows."""
import unittest
from regions import split_region


class RegionTests(unittest.TestCase):
    def test_full_resolution_and_partial_caps(self):
        for maximum in (159, 160, 161, 1024, 2560, 32000, 40960, 63999, 64000):
            with self.subTest(maximum=maximum):
                regions = {i: ((i % 8)*40, (i // 8)*40, (i % 8+1)*40, (i // 8+1)*40)
                           for i in range(40)}
                for _ in range(6):
                    for index, box in list(regions.items()):
                        boxes = split_region(box, maximum-len(regions))
                        regions[index] = boxes[0]
                        for child in boxes[1:]:
                            regions[len(regions)] = child
                    if len(regions) == maximum:
                        break
                self.assertEqual(len(regions), maximum)
                coverage = bytearray(64000)
                for x0,y0,x1,y1 in regions.values():
                    self.assertTrue(0 <= x0 < x1 <= 320 and 0 <= y0 < y1 <= 200)
                    for y in range(y0,y1):
                        for x in range(x0,x1):
                            coverage[y*320+x] += 1
                self.assertEqual(coverage, bytearray([1])*64000)
                if maximum == 64000:
                    self.assertTrue(all(x1-x0 == y1-y0 == 1 for x0,y0,x1,y1 in regions.values()))


if __name__ == '__main__':
    unittest.main()

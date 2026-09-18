import unittest
from model import DEMOS, State, linked


def window(x,y,w=300,h=240,workspace=5):
    return {'at':[x,y],'size':[w,h],'workspace':{'id':workspace}}


class Interactions(unittest.TestCase):
    def test_all_ten_geometry_and_outcomes(self):
        target=window(700,400,440,340)
        fixtures={'above':window(770,140),'below':window(770,760),
                  'left':window(380,450),'near':window(1190,440),
                  'contact':window(1145,440)}
        for index,demo in enumerate(DEMOS):
            with self.subTest(demo=demo.name):
                source=fixtures[demo.rule]
                self.assertTrue(linked(demo,source,target))
                self.assertFalse(linked(demo,window(-1000,-1000),target))
                other=dict(source,workspace={'id':6})
                self.assertFalse(linked(demo,other,target))
                s=State(index)
                for _ in range(500):s.step(.02,True)
                self.assertTrue(s.won)
                s.step(10,False)
                self.assertEqual(s.progress,1)
                s.reset();self.assertEqual(s.progress,0)

    def test_loss_of_alignment_reverses_temporary_effects(self):
        for index,demo in enumerate(DEMOS):
            s=State(index);s.step(.5,True);before=s.progress;s.step(.2,False)
            self.assertLessEqual(s.progress,before)
            if demo.decay:self.assertLess(s.progress,before)


if __name__=='__main__':unittest.main()

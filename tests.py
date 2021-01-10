import unittest
from Game import *


class TestMinimax(unittest.TestCase):

    def testXWin_1(self):
        g = Game('cpu', 'cpu')
        g.make_move((Mark('x', 1), 9, 1), [])
        g.make_move((Mark('o', 2), 2, 4), [])
        g.make_move((Mark('x', 3), 1, 5), [])
        result = g.run_minimax()
        self.assertTrue(result == 1.0)

    def testXWin_2(self):
        g = Game('cpu', 'cpu')
        g.make_move((Mark('x', 1), 1, 9), [])
        g.make_move((Mark('o', 2), 7, 3), [])
        g.make_move((Mark('x', 3), 7, 3), [])
        result = g.run_minimax()
        self.assertTrue(result == 0.5)

    def test_tie1(self):
        g = Game('cpu', 'cpu')
        g.make_move((Mark('x', 1), 1, 5), [])
        g.make_move((Mark('o', 2), 5, 1), [])
        g.make_move((Mark('o', 2), 5), [])
        result = g.run_minimax()
        self.assertTrue(result == 0)

    def test_lose(self):
        g = Game('cpu', 'cpu')
        g.make_move((Mark('x', 1), 2, 4), [])
        g.make_move((Mark('o', 2), 3, 7), [])
        g.make_move((Mark('x', 3), 3, 7), [])
        result = g.run_minimax()
        self.assertTrue(result == -1)

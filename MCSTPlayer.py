from GameTree import *
import random
import math
import time
import numpy as np


def search(root, max_time, C):
    start_time = time.time()
    while time.time() - start_time <= max_time or not root.is_expanded():
        new_node = selection(root, C)
        new_value = simulate(new_node, root.label)
        update(new_node, new_value)
    return best_candidate(root, C)[0]


def expand(node: GameNode):
    if node.leaf:
        node.add_child_nodes()
        assert not node.leaf
    for i, c in enumerate(node.children):
        if c[1] == None:
            return node.create_child_node(i, c[0])


def best_candidate(node: GameNode, C: float):
    vals = np.zeros(len(node.children))
    for i, c in enumerate(node.children):
        vals[i] = c[1].V + C * math.sqrt(math.log(node.N, math.e) / c[1].N)
    return node.children[np.argmax(vals)]


def selection(node: GameNode, C: float):
    while not node.leaf:
        if not node.is_expanded():
            new_node = expand(node)
            return new_node
        else:
            node = best_candidate(node, C)[1]
    return node


def simulate(node: GameNode, root_label: str):
    throwaway_board = node.board.copy()
    label = node.label
    while not throwaway_board.terminal_test():
        all_moves = throwaway_board.all_moves(label)
        if not all_moves:
            assert False
        new_move = random.choice(all_moves)
        throwaway_board.make_move(new_move)
        label = 'x' if label == 'o' else 'o'
    return throwaway_board.score()[0] if root_label == 'x' else -throwaway_board.score()[0]


def update(new_node: GameNode, value: float):
    while new_node:
        new_node.N += 1
        new_node.V += value
        new_node = new_node.parent


if __name__ == '__main__':
    g = GameTree('x')
    move = search(g.root, 20, 1.8)
    print(move)
from Board import *

class GameTree:
    def __init__(self, board, label):
        self.root = GameNode(board, None, None, label, 'x' if label == 'o' else 'o')
        self.root.add_child_nodes()

class GameNode:
    def __init__(self, node, parent_node, origin_move, label, opponent_label):
        self.board = node
        self.parent = parent_node
        self.origin_move = origin_move
        self.label = label
        self.opponent_label = opponent_label
        self.expanded_children = 0
        self.children = []
        self.leaf = True
        self.N = 0
        self.V = 0

    def is_expanded(self):
        return len(self.children) == self.expanded_children

    def add_child_nodes(self):
        if not self.board.terminal_test():
            self.leaf = False
            move_list = self.board.all_moves(self.label)
            for move in move_list:
                self.children.append([move, None])

    def create_child_node(self, index, move):
        new_board = self.board.copy()
        new_board.make_move(move)
        new_node = GameNode(new_board, self, move, self.opponent_label, self.label)
        self.children[index][1] = new_node
        self.expanded_children += 1
        return new_node

    def find_winning_move(self):
        pass

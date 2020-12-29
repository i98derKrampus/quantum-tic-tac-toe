from copy import deepcopy

import networkx as nx
import matplotlib.pyplot as plt


class Mark:
    def __init__(self, label, turn):
        self.label = label
        self.turn = turn

    def __iter__(self):
        yield self.label
        yield self.turn

    def __eq__(self, other):
        return self.label == other.label and self.turn == other.turn
    
    def __repr__(self):
        return "Mark({},{})".format(self.label,self.turn)


class Board:
    def __init__(self):
        self.entanglement = nx.Graph()
        self.board = {k: [] for k in range(1, 10)}

        self.collapsed = [False for k in range(10)]
        self.moves = []
        self.should_collapse = False
        self.collapse_at = None
        self.turn = 1
        self.cycle2 = False

    def _get_cycles(self):
        for cycle in list(nx.cycle_basis(self.entanglement)):
            return [
                (
                    node1,
                    node2,
                    self.entanglement.get_edge_data(node1, node2)
                )
                for node1, node2 in zip(cycle, (*cycle[1:], cycle[0]))
            ]

    def make_move(self, move):
        if self.should_collapse:
            mark, pos = move
            self.collapse(mark, pos, [])
            self.should_collapse = False
        else:
            mark, pos1, pos2 = move
            self.inscribe(mark, pos1, pos2)
            self.turn += 1
        self.moves.append(move)

    def all_moves(self, label):
        move_list = []
        if self.should_collapse:
            mark, pos1, pos2 = self.moves[-1]
            positions = [pos1, pos2]
            for p in positions:
                move_list.append((mark, p))
        else:
            seen = set()
            for i in range(1, 10):
                for j in range(1, 10):
                    if (i, j) not in seen and self.valid(Mark(label, self.turn), str(i), str(j)):
                        move_list.append((Mark(label, self.turn), i, j))
                        seen.add((i, j))
                        seen.add((j, i))
        return move_list

    def is_collapsed(self, *args):
        return all([self.collapsed[arg] for arg in args])

    def collapse(self, mark: Mark, pos_key: int, move_list: list):  # choose fate for first element in cycle
        self.board[pos_key] = [mark]
        self.collapsed[pos_key] = True

        if self.cycle2:
            self.cycle2 = False

        if not self.entanglement.edges(pos_key):
            return

        while True:
            neighbours = list(self.entanglement.edges(pos_key))
            if not neighbours:
                break

            node1, node2 = neighbours[0]
            edge_mark = self.entanglement.get_edge_data(node1, node2)['mark']
            move_list.append((edge_mark, node1, node2))

            self.entanglement.remove_edge(node1, node2)

            self.collapse(edge_mark, node2, move_list)

    def inscribe(self, mark: Mark, pos_key1: int, pos_key2: int):
        self.board[pos_key1].append(mark)
        self.board[pos_key2].append(mark)

        if self.entanglement.has_edge(pos_key1, pos_key2):
            self.should_collapse = True
            self.collapse_at = pos_key1
            self.cycle2 = True
            return

        self.entanglement.add_edge(pos_key1, pos_key2, mark=mark)
        self.should_collapse = not not self._get_cycles()  # False if cycle list is empty

        if self.should_collapse:
            self.collapse_at = pos_key1

    def score(self):
        three, maxs = self.three_in_a_row()
        if not any(three):
            score = (0, 0)
        elif three[0] and not three[1]:
            score = (1, 0)
        elif three[1] and not three[0]:
            score = (0, 1)
        elif maxs[0] < maxs[1]:
            score = (1, 0.5)
        else:
            score = (0.5, 1)
        return score[0] - score[1], "The game ended with score {}-{}".format(*score)

    def three_in_a_row(self):
        three = [False, False]  # three in a row for player 1, 2
        maxs = [10, 10]

        for i in [(1, 2, 3), (4, 5, 6), (7, 8, 9),
                  (1, 4, 7), (2, 5, 8), (3, 6, 9),
                  (1, 5, 9), (3, 5, 7)]:

            if self.is_collapsed(*i):
                mark1 = self.board[i[0]][0]
                mark2 = self.board[i[1]][0]
                mark3 = self.board[i[2]][0]

                if all(x.label == mark1.label for x in [mark1, mark2, mark3]):
                    if mark1.label == "x":
                        maxs[0] = max([self.board[k][0].turn for k in i])
                        three[0] = True
                    else:
                        maxs[1] = max([self.board[k][0].turn for k in i])
                        three[1] = True

        return three, maxs

    def terminal_test(self):
        score, _ = self.score()
        return all(self.collapsed[1:]) or score != 0

    def valid(self, mark, pos_key1, pos_key2=None):
        """
        :param mark: mark to place
        :param pos_key1: position key of the first field to mark
        :param pos_key2: position key of the second field to mark or None if the turn is to collapse
        :return: True if the move:
                    inscribe mark to pos_key1 and pos_key2 or collapse with mark at pos_key1
                 is valid

        promjene:
        move -> pos_key da budu iste oznake svugdje
        ovdje sam stavila None jer se bunio na 0 (ocekuje string)
        i kod provjere sam onda gledala je li pos_key2 < 1 jer 0 isto nije ok a to ne bi uhvatio
        """
        if not pos_key1.isdigit() or (pos_key2 and not pos_key2.isdigit()):
            return False

        turn_mark = pos_key2
        pos_key1, pos_key2 = int(pos_key1), pos_key2 and int(pos_key2)

        #  position keys should be in {1, ..., 9}
        if pos_key1 < 1 or pos_key1 > 9 or (turn_mark and (pos_key2 < 1 or pos_key2 > 9)):
            return False

        # the board shouldn't be collapsed at the specified position keys
        if self.is_collapsed(pos_key1) or \
                (turn_mark and pos_key1 != pos_key2 and self.is_collapsed(pos_key2)):
            return False

        if turn_mark:
            if pos_key1 == pos_key2:
                if mark.turn != 9:
                    return False

                indices = list(range(1, 10))
                indices.remove(pos_key1)
                return self.is_collapsed(*indices)
            else:
                return True
        else:  # collapse (with assumption there actually is a cycle)
            """
               check for:
                    (1) there is a mark at the specified position key
                    (2) the mark selected for inscription to that position is present in ghost marks 
            """
            return pos_key1 in self.board and mark in self.board[pos_key1]

    def undo_move(self, move):
        mark, pos1, pos2 = move
        self.turn -= 1
        if not self.cycle2:
            self.entanglement.remove_edge(pos1, pos2)
        else:
            self.cycle2 = False
        self.board[pos1].remove(mark)
        self.board[pos2].remove(mark)
        self.should_collapse = False
        self.collapse_at = None

    def undo_collapse(self, collapse_pos: int, move_list: list):
        self.board[collapse_pos] = []
        self.collapsed[collapse_pos] = False
        move_list.reverse()
        for move in move_list:
            mark, pos1, pos2 = move

            if self.entanglement.has_edge(pos1, pos2):
                self.cycle2 = True
                self.board[pos1].append(mark)
                self.board[pos2].append(mark)
                continue

            self.entanglement.add_edge(pos1, pos2, mark=mark)
            if self.collapsed[pos1]:
                self.board[pos1] = []
                self.collapsed[pos1] = False
            if self.collapsed[pos2]:
                self.board[pos2] = []
                self.collapsed[pos2] = False
            self.board[pos1].append(mark)
            self.board[pos2].append(mark)

    def copy(self):
        new_board = Board()
        new_board.board = deepcopy(self.board)
        new_board.entanglement = deepcopy(self.entanglement)
        new_board.collapsed = deepcopy(self.collapsed)
        new_board.moves = deepcopy(self.moves)
        new_board.should_collapse = self.should_collapse
        new_board.collapse_at = self.collapse_at
        new_board.turn = self.turn
        new_board.cycle2 = self.cycle2
        return new_board

    def show_entanglement(self):
        cycles = list(nx.cycle_basis(self.entanglement))

        draw = nx.circular_layout(self.entanglement)

        nx.draw_networkx(self.entanglement, pos=draw, with_labels=True)
        nx.draw_networkx_edge_labels(self.entanglement,
                                     draw,
                                     edge_labels=
                                     {e: tuple(self.entanglement.get_edge_data(*e)['mark'])
                                      for e in self.entanglement.edges()},
                                     font_color='green')
        nx.draw_networkx_edges(self.entanglement,
                               pos=draw,
                               edgelist=[
                                   (cycle[n],
                                    cycle[(n + 1) % len(cycle)]
                                    )
                                   for cycle in cycles
                                   for n in range(len(cycle))
                               ],

                               edge_color='r',
                               width=3)

        plt.show()

    def show_board(self):
        for i in range(9):
            if not i%3:
                print("$"*50)
            row = "$$"

            for j in range(1, 4):
                field = ""
                for m in self.board[i//3*3+j][3*(i%3):3*(i%3+1)]:
                    field += f"{m.label}{m.turn} "
                field = field[:-1].center(14) + "$$"
                row += field
            print(row)
        print("$"*50)
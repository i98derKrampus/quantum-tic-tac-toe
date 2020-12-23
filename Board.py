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
        self.should_collapse = False
        self.collapse_at = None

        self.turn = 0

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

    def is_collapsed(self, *args):
        return all([self.collapsed[arg] for arg in args])

    def collapse(self, mark: Mark, pos_key: int):  # choose fate for first element in cycle
        self.board[pos_key] = [mark]
        self.collapsed[pos_key] = True

        if not self.entanglement.edges(pos_key):
            return

        while True:
            neighbours = list(self.entanglement.edges(pos_key))
            if not neighbours:
                break

            node1, node2 = neighbours[0]
            edge_mark = self.entanglement.get_edge_data(node1, node2)['mark']

            self.entanglement.remove_edge(node1, node2)

            self.collapse(edge_mark, node2)

    def inscribe(self, mark: Mark, pos_key1: int, pos_key2: int):
        self.board[pos_key1].append(mark)
        self.board[pos_key2].append(mark)

        if self.entanglement.has_edge(pos_key1, pos_key2):
            self.should_collapse = True
            self.collapse_at = pos_key1
            return

        self.entanglement.add_edge(pos_key1, pos_key2, mark=mark)
        self.should_collapse = not not self._get_cycles()  # False if cycle list is empty

        if self.should_collapse:
            self.collapse_at = pos_key1

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
        for i in range(1, 10):
            for m in self.board[i]:
                print(f"{m.label}{m.turn}", end=" ")
            print('\t\t', end=" ")

            if not i % 3:
                print('\n')


class Player(Board):
    def __init__(self, player_type, board, label, turn):
        self.label = label
        self.player_type = player_type

        super(Player, self).__init__()

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
        if pos_key1 < 1 or pos_key1 > 9 or (turn_mark and pos_key2 < 1 or pos_key2 > 9):
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

        else:  # collapse (with assumption there actually is a cycle)
            """
               check for:
                    (1) there is a mark at the specified position key
                    (2) the mark selected for inscription to that position is present in ghost marks 
            """
            return pos_key1 in self.board and mark in self.board[pos_key1]

    def play_collapse(self):
        self.show_board()  # maybe just this? idk
        label = 'x' if self.label == 'o' else 'o'

        invalid = True
        while invalid:
            move = input(f"Collapse {label}{self.turn - 1}: ")
            invalid = not self.valid(Mark(label, self.turn - 1), move)

        return Mark(label, self.turn - 1), int(move)

    def play_mark(self):
        self.show_board()

        invalid = True
        while invalid:
            move = input(f"Place {self.label}{self.turn}: ").split()

            if len(move) > 1:
                invalid = not self.valid(Mark(self.label, self.turn), move[0], move[1])

        return Mark(self.label, self.turn), int(move[0]), int(move[1])


class Bot(Player):
    def __init__(self, board, label, turn):
        super().__init__("cpu", board, label, turn)

    def play_collapse(self):
        """
        :return:
        """
        return "Mark(l, self.turn-1), pos"

    def play_mark(self):
        """
        :return:
        """
        return "Mark(self.label, self.turn), pos1, pos2"


class Game(Board):
    def __init__(self, player1="human", player2="cpu"):
        self.players = [Player(player1, self.board, 'x', 0), Player(player2, self.board, 'o', 0)]
        self.turn = 0
        super(Game, self).__init__()

    def game_over(self):
        return self.score()[0]

    def score(self):
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
        return score[0] == score[1], "The game ended with score {}-{}".format(*score)

    def run(self):
        cycle2 = False

        for turn in range(self.turn, 10):
            if self.game_over():
                break

            if cycle2 or self.should_collapse:
                move = self.players[turn % 2].play_collapse()
                self.collapse(move[0], move[1])

            if turn == 9 or self.game_over():  # game ended with collapse
                break

        m = None
        for turn in range(self.turn, 10):
            if self.game_over():
                break
            self.players[turn%2].update(self.board, turn+1)
            if cycle2 or self.board.should_collapse():
                move = self.players[turn%2].collapse()
                self.board.collapse(move[0], move[1])
                if cycle2:
                    if move[1] == m[1]:
                        self.board.board[m[2]][0] = m[0]
                    else:
                        self.board.board[m[1]][0] = m[0]
                self.players[turn%2].update(self.board, turn+1)
            if turn == 9 or self.game_over(): #game ended with collapse
                break
            move = self.players[turn%2].mark()
            cycle2 = self.board.entanglement.has_edge(move[1],move[2])
            if cycle2:
                m = [self.board.entanglement.get_edge_data(move[1], move[2])['mark'], move[1], move[2]]
            self.board.inscribe(*move)

            move = self.players[turn % 2].play_mark()
            cycle2 = self.entanglement.has_edge(move[1], move[2])
            self.inscribe(*move)

        self.show_board()
        print("Game over: " + self.score()[1])


if __name__ == '__main__':
    b = Board()

    #b.inscribe(Mark('x', 1), 1, 3)
    #b.inscribe(Mark('o', 2), 2, 3)
    #b.inscribe(Mark('x', 3), 2, 4)
    #b.inscribe(Mark('o', 4), 4, 5)
    #b.inscribe(Mark('x', 5), 3, 4)

    print(b.should_collapse)
    # b.show_entanglement()
    b.show_board()

    b.collapse(Mark('x', 3), 2)
    print(b.should_collapse)
    # b.show_entanglement()
    b.show_board()

    #print(b.should_collapse())
    #b.show_entanglement()
    #b.show_board()

    #b.collapse(Mark('x', 3), 2)
    #print(b.should_collapse())
    #b.show_entanglement()
    #b.show_board()

    game = Game("human", "human")
    game.run()

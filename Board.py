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


class Board:
    def __init__(self):
        self.entanglement = nx.Graph()
        self.board = {k: [] for k in range(1, 10)}

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

    def should_collapse(self):
        return not not self._get_cycles()  # False if cycle list is empty

    def collapse(self, mark: Mark, pos_key: int):  # choose fate for first element in cycle
        self.board[pos_key] = [mark]

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
        self.entanglement.add_edge(pos_key1, pos_key2, mark=mark)
        self.board[pos_key1].append(mark)
        self.board[pos_key2].append(mark)

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
        for i in range(1,10):
            for m in self.board[i]:
                print(f"{m.label}{m.turn}", end=" ")
            print('\t\t', end=" ")

            if not i % 3:
                print('\n')


if __name__ == '__main__':
    b = Board()

    b.inscribe(Mark('x', 1), 1, 3)
    b.inscribe(Mark('o', 2), 2, 3)
    b.inscribe(Mark('x', 3), 2, 4)
    b.inscribe(Mark('o', 4), 4, 5)
    b.inscribe(Mark('x', 5), 3, 4)

    print(b.should_collapse())
    b.show_entanglement()
    b.show_board()

    b.collapse(Mark('x', 3), 2)
    print(b.should_collapse())
    b.show_entanglement()
    b.show_board()

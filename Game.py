from Player import *
from MCSTPlayer import *
import time

class Game(Board):
    def __init__(self, player1="human", player2="cpu"):
        super().__init__()
        p1 = Bot(self, 'x') if player1 == 'cpu' else Player(player1, self, 'x')
        p2 = Bot(self, 'o') if player2 == 'cpu' else Player(player2, self, 'o')
        self.players = [p1, p2]

    def game_over(self):
        return self.score()[0] != 0 or all(self.collapsed[1:])

    def run_mcst(self):
        for turn in range(self.turn - 1, 10):
            if self.game_over():
                break

            if self.players[turn % 2].player_type == 'human':
                if self.should_collapse:
                    move = self.players[turn % 2].play_collapse()
                    print(f'Player {self.players[turn % 2].label} collapsed {move} in turn {self.turn}\n')
                    self.moves.append(move)
                    self.collapse(move[0], move[1], [])

                if turn == 9 or self.game_over():  # game ended with collapse
                    break

                move = self.players[turn % 2].play_mark()
                print(f'Player {self.players[turn % 2].label} played {move} in turn {self.turn}\n')
                self.moves.append(move)
                self.inscribe(*move)

            else:
                oplabel = 'x' if self.players[turn % 2].label == 'o' else 'o'
                if self.should_collapse:
                    g = GameTree(self, self.players[turn % 2].label)
                    move = search(g.root, 30 - 2.2 * turn, 1.8)
                    print(f'Player {self.players[turn % 2].label} collapsed {move} in turn {self.turn}\n')
                    self.make_move(move)

                if turn == 9 or self.game_over():  # game ended with collapse
                    break

                g = GameTree(self, self.players[turn % 2].label)
                move = search(g.root, 30 - 2.2 * turn, 1.8)
                print(f'Player {self.players[turn % 2].label} played {move} in turn {self.turn}\n')
                self.make_move(move)



            if turn == 9 or self.game_over():
                    break

            self.show_board()

        self.show_board()
        print("Game over: " + self.score()[1])

    def run_minimax(self):
        for turn in range(self.turn - 1, 10):
            if self.game_over():
                break

            if self.should_collapse:
                move = self.players[turn % 2].play_collapse()
                print(f'Player {self.players[turn % 2].label} collapsed {move} in turn {self.turn}\n')
                self.make_move(move, [])

            if turn == 9 or self.game_over():  # game ended with collapse
                break

            move = self.players[turn % 2].play_mark()
            print(f'Player {self.players[turn % 2].label} played {move} in turn {self.turn}\n')
            self.make_move(move, [])
            self.show_board()


        self.show_board()
        print("Game over: " + self.score()[1])
        return self.score()[0]

from Player import *
import time

class Game(Board):
    def __init__(self, player1="human", player2="cpu"):
        super().__init__()
        p1 = Bot(self, 'x') if player1 == 'cpu' else Player(player1, self, 'x')
        p2 = Bot(self, 'o') if player2 == 'cpu' else Player(player2, self, 'o')
        self.moves = []
        self.players = [p1, p2]

    def game_over(self):
        return self.score()[0] != 0 or all(self.collapsed[1:])

    def run(self):
        for turn in range(self.turn, 10):
            self.turn += 1
            if self.game_over():
                break

            if self.should_collapse:
                move = self.players[turn % 2].play_collapse()
                print(f'Player {self.players[turn % 2].label} collapsed {move} in turn {self.turn}\n')
                self.moves.append(move)
                self.collapse(move[0], move[1])

            if turn == 9 or self.game_over():  # game ended with collapse
                break

            move = self.players[turn % 2].play_mark()
            print(f'Player {self.players[turn % 2].label} played {move} in turn {self.turn}\n')
            self.moves.append(move)
            self.inscribe(*move)
            self.show_board()

        self.show_board()
        print("Game over: " + self.score()[1])


if __name__ == '__main__':
    new_game = Game("cpu", "cpu")
    new_game.inscribe(Mark('x', 1), 9, 1)
    new_game.inscribe(Mark('o', 2), 1, 5)
    new_game.turn = 2
    new_game.moves.append((Mark('x', 1), 9, 1))
    new_game.moves.append((Mark('o', 2), 1, 5))
    start_time = time.time()
    new_game.run()
    print(f'--------{time.time() - start_time} seconds ----------')

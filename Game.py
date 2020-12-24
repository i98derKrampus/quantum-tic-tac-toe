from Player import *


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
            print(turn)
            if self.game_over():
                break

            if self.should_collapse:
                move = self.players[turn % 2].play_collapse()
                self.moves.append(move)
                self.collapse(move[0], move[1])

            if turn == 9 or self.game_over():  # game ended with collapse
                break

            move = self.players[turn % 2].play_mark()
            self.moves.append(move)
            self.inscribe(*move)

        self.show_board()
        print("Game over: " + self.score()[1])


if __name__ == '__main__':
    new_game = Game("human", "cpu")
    new_game.run()

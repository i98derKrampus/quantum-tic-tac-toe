from Board import *
from MCSTPlayer import *


class Player:
    def __init__(self, player_type, game, label):
        self.label = label
        self.player_type = player_type
        self.game = game

    def play_collapse(self):
        label = 'x' if self.label == 'o' else 'o'

        invalid, move = True, None
        while invalid:
            move = input(f"Collapse {label}{self.game.turn - 1}: \n")
            invalid = not self.game.valid(Mark(label, self.game.turn - 1), move)

        return Mark(label, self.game.turn - 1), int(move)

    def play_mark(self):
        invalid, move = True, None
        while invalid:
            move = input(f"Place {self.label}{self.game.turn}: \n").split()

            if len(move) > 1:
                invalid = not self.game.valid(Mark(self.label, self.game.turn), move[0], move[1])

        return Mark(self.label, self.game.turn), int(move[0]), int(move[1])

    def opponent_label(self):
        if self.label == 'x':
            return 'o'
        return 'x'


class Bot(Player):
    def __init__(self, game, label):
        super().__init__("cpu", game, label)
        self.__minimax_board = game.copy()
        self.cpy_time = 0

    def play_collapse(self):
        last_move = self.game.moves[-1]
        self.__minimax_board = self.game.copy()
        alpha, beta = -2, 2
        score, move = self.__minimax_collapse(alpha, beta, last_move, self.label == 'x')
        return move

    def play_mark(self):
        alpha, beta = -2, 2
        self.__minimax_board = self.game.copy()
        score, move = self.__minimax_mark(alpha, beta, self.label == 'x')
        print(score)
        return move

    def __minimax_collapse(self, alpha, beta, last_move, is_max):
        return_move = None
        if self.game.terminal_test():
            return self.__minimax_board.score()[0], return_move

        score = -3 if is_max else 3
        mark, pos1, pos2 = last_move

        positions = [pos1, pos2]
        for p in positions:
            move_list = []

            if self.__minimax_board.cycle2:
                move_list.append(last_move)

            candidate_move = (mark, p)
            self.__minimax_board.make_move(candidate_move, move_list)

            candidate_score, _ = self.__minimax_mark(alpha, beta, is_max)
            self.__minimax_board.undo_collapse(p, move_list)

            if is_max:
                if score < candidate_score:
                    score, return_move = candidate_score, candidate_move
                alpha = max(score, alpha)
            else:
                if score > candidate_score:
                    score, return_move = candidate_score, candidate_move
                beta = min(score, beta)

            if beta <= alpha:
                return score, return_move

        return score, return_move

    def __minimax_mark(self, alpha, beta, is_max):
        return_move = None
        label = 'x' if is_max else 'o'

        if self.__minimax_board.terminal_test():
            return self.__minimax_board.score()[0], return_move

        score = -3 if is_max else 3
        seen = set()
        for i in [1, 3, 5, 7, 9, 2, 4, 6, 8]:
            for j in [5, 1, 3, 7, 9, 2, 4, 6, 8]:
                if (i, j) in seen: continue
                seen.add((i, j))
                seen.add((j, i))
                if self.__minimax_board.valid(Mark(self.label, self.__minimax_board.turn), str(i), str(j)):
                    candidate_move = (Mark(label, self.__minimax_board.turn), i, j)
                    self.__minimax_board.make_move(candidate_move, [])

                    if self.__minimax_board.should_collapse:
                        candidate_score, _ = self.__minimax_collapse(alpha, beta, candidate_move, not is_max)
                    else:
                        candidate_score, _ = self.__minimax_mark(alpha, beta, not is_max)

                    self.__minimax_board.undo_move(candidate_move)

                    if is_max:
                        if score < candidate_score:
                            score, return_move = candidate_score, candidate_move
                        alpha = max(alpha, score)

                    else:
                        if score > candidate_score:
                            score, return_move = candidate_score, candidate_move
                        beta = min(beta, score)

                    if alpha >= beta:
                        return score, return_move

        return score, return_move

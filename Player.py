from Board import *


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

    def play_collapse(self):
        last_move = self.game.moves[-1]
        self.__minimax_board = self.game.copy()
        alpha, beta = -3, 3
        score, move = self.__minimax_collapse(alpha, beta, last_move, self.label == 'x')
        return move

    def play_mark(self):
        alpha, beta = -3, 3
        self.__minimax_board = self.game.copy()
        score, move = self.__minimax_mark(alpha, beta, self.label == 'x')
        return move

    def __minimax_collapse(self, alpha, beta, last_move, is_max):
        return_move = None
        if self.terminal_test():
            return self.__minimax_board.score()[0], return_move

        score = -4 if is_max else 4
        mark, pos1, pos2 = last_move
        positions = [pos1, pos2]
        temp_board = self.__minimax_board.copy()
        for p in positions:
            candidate_move = (mark, p)
            self.__minimax_board.collapse(mark, p)
            if is_max:
                candidate_score, _ = self.__minimax_mark(alpha, beta, is_max)
                if score < candidate_score:
                    score = candidate_score
                    return_move = candidate_move

                self.__minimax_board = temp_board.copy()
                if score >= beta:
                    return score, return_move
                alpha = max(score, alpha)

            else:
                candidate_score, _ = self.__minimax_mark(alpha, beta, is_max)
                if score > candidate_score:
                    score = candidate_score
                    return_move = candidate_move

                self.__minimax_board = temp_board.copy()
                if score <= alpha:
                    return score, return_move

                beta = min(score, beta)

        return score, return_move

    def __minimax_mark(self, alpha, beta, is_max):
        return_move = None
        label = 'x' if is_max else 'o'
        if self.terminal_test():
            return self.__minimax_board.score()[0], return_move

        score = -4 if is_max else 4
        seen = set()
        for i in [1, 3, 7, 9]:
            for j in [1, 3, 7, 9]:
                if (i, j) in seen: continue
                score, alpha, beta, return_move = self.__expand(i, j, alpha, beta, is_max, label, score, return_move,
                                                                seen)
                if is_max and score >= beta:
                    return score, return_move
                elif not is_max and score <= alpha:
                    return score, return_move

            j = 5
            if (i, j) in seen: continue
            score, alpha, beta, return_move = self.__expand(i, j, alpha, beta, is_max, label, score, return_move,
                                                            seen)
            if is_max and score >= beta:
                return score, return_move
            elif not is_max and score <= alpha:
                return score, return_move

            for j in [2, 4, 6, 8]:
                if (i, j) in seen: continue
                score, alpha, beta, return_move = self.__expand(i, j, alpha, beta, is_max, label, score, return_move,
                                                                seen)
                if is_max and score >= beta:
                    return score, return_move
                elif not is_max and score <= alpha:
                    return score, return_move
        i = 5
        j = 5
        if (i, j) not in seen:
            score, alpha, beta, return_move = self.__expand(i, j, alpha, beta, is_max, label, score, return_move, seen)
            if is_max and score >= beta:
                return score, return_move
            elif not is_max and score <= alpha:
                return score, return_move

        for j in [2, 4, 6, 8]:
            if (i, j) in seen: continue
            score, alpha, beta, return_move = self.__expand(i, j, alpha, beta, is_max, label, score, return_move, seen)
            if is_max and score >= beta:
                return score, return_move
            elif not is_max and score <= alpha:
                return score, return_move


        for i in [2, 4, 6, 8]:
            for j in [2, 4, 6, 8]:
                if (i, j) in seen: continue
                score, alpha, beta, return_move = self.__expand(i, j, alpha, beta, is_max, label, score, return_move,
                                                                seen)
                if is_max and score >= beta:
                    return score, return_move
                elif not is_max and score <= alpha:
                    return score, return_move

        return score, return_move

    def __expand(self, pos1, pos2, alpha, beta, is_max, label, score, return_move, seen):
        if self.__minimax_board.valid(Mark(self.label, self.__minimax_board.turn), str(pos1), str(pos2)):
            seen.add((pos1, pos2))
            seen.add((pos2, pos1))
            temp_board = self.__minimax_board.copy()
            self.__minimax_board.inscribe(Mark(label, self.__minimax_board.turn), pos1, pos2)
            candidate_move = (Mark(label, self.__minimax_board.turn), pos1, pos2)
            self.__minimax_board.turn += 1
            if is_max:
                if self.__minimax_board.should_collapse:
                    candidate_score, _ = self.__minimax_collapse(alpha, beta, candidate_move, not is_max)
                    if score < candidate_score:
                        score, return_move = candidate_score, candidate_move

                else:
                    candidate_score, _ = self.__minimax_mark(alpha, beta, not is_max)
                    if score < candidate_score:
                        score, return_move = candidate_score, candidate_move

                self.__minimax_board = temp_board.copy()
                if score >= beta:
                    return score, alpha, beta, return_move

                alpha = max(alpha, score)

            else:
                if self.__minimax_board.should_collapse:
                    candidate_score, _ = self.__minimax_collapse(alpha, beta, candidate_move, not is_max)
                    if score > candidate_score:
                        score, return_move = candidate_score, candidate_move
                else:
                    candidate_score, _ = self.__minimax_mark(alpha, beta, not is_max)
                    if score > candidate_score:
                        score, return_move = candidate_score, candidate_move

                self.__minimax_board = temp_board.copy()
                if score <= alpha:
                    return score, alpha, beta, return_move
                beta = min(beta, score)

        return score, alpha, beta, return_move

    def terminal_test(self):
        score, _ = self.__minimax_board.score()
        return all(self.__minimax_board.collapsed[1:]) or score != 0

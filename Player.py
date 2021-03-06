from Board import *
import re


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
        if self.game.turn == 3:
            p = self.__get_from_file()
            return (Mark('o', 2), p)

        last_move = self.game.moves[-1]
        self.__minimax_board = self.game.copy()
        alpha, beta = -2, 2
        score, move = self.__minimax_collapse(alpha, beta, last_move, self.label == 'x')
        return move

    def play_mark(self):
        if self.game.turn == 1:
            return (Mark(self.label, self.game.turn), 1, 9)

        if self.game.turn == 2:
            mark, pos1, pos2 = self.game.moves[-1]
            move_dict = self.__get_from_file()
            npos1, npos2 = move_dict[(pos1, pos2)][0]
            return (Mark(self.label, self.game.turn), npos1, npos2)

        if self.game.turn == 3:
            p1, p2 = self.__get_from_file()
            return (Mark(self.label, self.game.turn), p1, p2)

        alpha, beta = -2, 2
        self.__minimax_board = self.game.copy()
        score, move = self.__minimax_mark(alpha, beta, self.label == 'x')
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

            if self.__cutoff(is_max, score, alpha, beta):
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

                    if self.__cutoff(is_max, score, alpha, beta):
                        return score, return_move

        return score, return_move

    def __cutoff(self, is_max, score, alpha, beta):
        if alpha >= beta:
            return True
        elif (is_max and score == 1) or (not is_max and score == -1):
            return True
        return False

    def __get_from_file(self):
        if self.game.turn == 2:
            with open('assets/second_move_optimal') as f:
                lines = [x.strip() for x in f.readlines()]

            d = dict()
            curr_key, rcurr_key = None, None
            for line in lines:
                x = line.split(',')
                if x == ['']:
                    continue

                ints = [int(x) for x in re.findall(r'\d+', line)]
                if line.startswith('('):
                    curr_key = (ints[0], ints[1])
                    rcurr_key = (ints[1], ints[0])
                    d[curr_key], d[rcurr_key] = [], []
                else:
                    d[curr_key].append((ints[0], ints[1]))
                    d[rcurr_key].append((ints[0], ints[1]))
            return d
        elif self.game.turn == 3:
            with open('assets/third_move_optimal') as f:
                lines = [x.strip() for x in f.readlines()]

            moves = []
            for i in range(2):
                mark, p1, p2 = self.game.moves[i]
                moves.append((p1, p2))
            if len(self.game.moves) == 3:
                mark, p = self.game.moves[-1]
                if mark.label == 'x':
                    moves.append(p)
                else:
                    mark2, pos1, pos2 = self.game.moves[-2]
                    if p == pos1:
                        moves.append(pos2)
                    else:
                        moves.append(pos1)

            pairs = None
            for line in lines:
                x = line.split(',')
                if x == ['']:
                    continue
                ints = [int(x) for x in re.findall(r'\d+', line)]
                if line.startswith('('):
                    pairs = []
                    pairs.append((ints[0], ints[1]))
                    pairs.append((ints[2], ints[3]))
                    if len(ints) == 5:
                        pairs.append(ints[4])

                else:
                    if len(pairs) != len(moves):
                        continue
                    m1, m2 = moves[0], moves[1]
                    p1, p2 = m1
                    p3, p4 = m2
                    if ((p1, p2) == pairs[0] or (p2, p1) == pairs[0]) and ((p3, p4) == pairs[1] or (p4, p3) == pairs[1]):
                        if len(moves) == 3:
                            if moves[-1] == pairs[-1]:
                                return ints[0], ints[1]
                        else:
                            if self.game.should_collapse:
                                if p1 == ints[0]:
                                    return p2
                                return p1
                            return ints[0], ints[1]

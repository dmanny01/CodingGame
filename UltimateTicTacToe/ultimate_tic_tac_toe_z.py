import sys
import math
from enum import Enum
from copy import deepcopy
import datetime, random

# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.
def debug(*args, **kwargs):
    print(*args, **kwargs, file=sys.stderr)

Player = Enum('Player', 'P1 P2')
ALL_P1 = [1,1,1]
ALL_P0 = [0,0,0]

class Board9:

    def __init__(self):
        self.size = 3
        self.boards = [[Board(3) for _ in range(3)] for _ in range(3)]
        self.win_board = [[-1 for _ in range(3)] for _ in range(3)]
        self.next_player = 1
        self.moves = list()
        self.all_moves = [[list() for _ in range(3)] for _ in range(3)]

        for i in range(9):
            for j in range(9):
                board_r, board_c = i // 3, j // 3
                x, y = i % 3, j % 3
                self.all_moves[board_r][board_c].append((i, j))

    def legal_moves(self):
        return self.moves

    def add_legal_move(self, move):
        self.moves.append(move)

    def clear_legal_moves(self):
        self.moves.clear()

    def current_player(self):
        return self.next_player

    def next_state(self, move):
        i, j = move
        board_r, board_c = i//3, j//3
        x, y = i%3, j%3
        active_board = self.boards[board_r][board_c]
        active_board.matrix[x][y] = self.next_player
        result = self.compact_state()
        active_board.matrix[x][y] = -1
        return result

    def play(self, move):
        # self.moves.remove(move) if self.next_player == 1 else None
        # debug(f'Moves: {move}')
        i, j = move
        board_r, board_c = i // 3, j // 3
        x, y = i % 3, j % 3
        # debug(f'br,bc {i},{j} | x,y: {x},{y}')
        active_board = self.boards[board_r][board_c]
        active_board.matrix[x][y] = self.next_player
        self.next_player ^= 1
        self.clear_legal_moves()
        self.all_moves[board_r][board_c].remove(move)
        self.moves = deepcopy(self.all_moves[x][y])

    def compact_state(self):
        result = ''
        for rboards in self.boards:
            for board in rboards:
                result += board.compact_state()
        return result

    def winner(self):
        for i, rboards in enumerate(self.boards):
            for j, board in enumerate(rboards):
                result = board.winner()
                if result == 0 or result == 1:
                    self.win_board[i][j] = result
        #debug(f'WinBoard: {self.win_board}')
        #self.print()

        for i in range(self.size):  # check rows n columns
            if self.win_board[i] == ALL_P1 or self.win_board[:][i]== ALL_P1:
                return 1  # Player 1
            elif self.win_board[i] == ALL_P0 or self.win_board[:][i] == ALL_P0:
                return 0  # Player 0

        diag = [r[i] for i, r in enumerate(self.win_board)]
        rdiag = [r[-i-1] for i, r in enumerate(self.win_board)]
        if diag == ALL_P1 or rdiag == ALL_P1:
            return 1 # Player 1
        elif diag == ALL_P0 or rdiag == ALL_P0:
            return 0 # Player 0

        ones = sum([row.count(1) for row in self.win_board])
        zeros = sum([row.count(0) for row in self.win_board])
        return 1 if ones >= 5 else 0 if zeros >= 5 else -1

    def print(self):
        for i, rboards in enumerate(self.boards):
            debug(str(rboards))
                

class Board:
    def __init__(self, size):
        self.matrix = [[-1 for _ in range(size)] for _ in range(size)]
        self.size = size
        self._winner = None

    def winner(self):
        if self._winner and not self._winner == -1:
            return self._winner

        for i in range(self.size):  # check rows n columns
            if self.matrix[i] == ALL_P1 or self.matrix[:][i] == ALL_P1:
                return 1  # Player 1
            elif self.matrix[i] == ALL_P0 or self.matrix[:][i] == ALL_P0:
                return 0  # Player 0

        diag = [r[i] for i, r in enumerate(self.matrix)]
        rdiag = [r[-i-1] for i, r in enumerate(self.matrix)]
        if diag == ALL_P1 or rdiag == ALL_P1:
            return 1 # Player 1
        elif diag == ALL_P0 or rdiag == ALL_P0:
            return 0 # Player 0
        '''
        ones = sum([row.count(1) for row in self.matrix])
        zeros = sum([row.count(0) for row in self.matrix])
        return 1 if ones >= 5 else 0 if zeros >= 5 else -1
        '''
        return -1

    def compact_state(self):
        result = ''
        for i, row in enumerate(self.matrix):
            for j, val in enumerate(row):
                result += str(val)
        return result

    def __repr__(self):
        return str(self.matrix)


class MCTS:
    def __init__(self, board, **kwargs):
        self.board = board
        mseconds = kwargs.get('time', 900)
        self.calculation_time = datetime.timedelta(milliseconds=mseconds)
        self.max_moves = kwargs.get('max_moves', 1000)
        self.C = kwargs.get('C', 100)
        self.plays = dict()
        self.wins = dict()

    def update_param(self, **kwargs):
        mseconds = kwargs.get('time', 70)
        self.calculation_time = datetime.timedelta(milliseconds=mseconds)
        self.max_moves = kwargs.get('max_moves', 9)


    def get_play(self):
        self.max_depth = 0
        state = self.board.compact_state()
        player = self.board.current_player()
        legal = self.board.legal_moves()

        # Bail out early if there is no real choice to be made.
        if not legal:
            return
        if len(legal) == 1:
            return legal[0]

        games = 0
        begin = datetime.datetime.utcnow()
        while datetime.datetime.utcnow() - begin < self.calculation_time:
            self.run_simulation()
            games += 1

        moves_states = [(p, self.board.next_state(p)) for p in legal]

        # Display the number of calls of `run_simulation` and the
        # time elapsed.
        # print games, datetime.datetime.utcnow() - begin

        # Pick the move with the highest percentage of wins.
        percent_wins, move = max(
            (self.wins.get((player, S), 0) /
             self.plays.get((player, S), 1),
             p)
            for p, S in moves_states
        )

        # Display the stats for each possible play.
        for x in sorted(
            ((100 * self.wins.get((player, S), 0) /
              self.plays.get((player, S), 1),
              self.wins.get((player, S), 0),
              self.plays.get((player, S), 0), p)
             for p, S in moves_states),
            reverse=True
        ):
            debug("{3}: {0:.2f}% ({1} / {2})".format(*x))

        debug(f"Maximum depth searched: {self.max_depth}")

        return move



    def run_simulation(self):
        # A bit of an optimization here, so we have a local
        # variable lookup instead of an attribute access each loop.
        plays, wins = self.plays, self.wins

        visited_states = set()
        vboard = deepcopy(self.board)
        states_copy = vboard.compact_state()
        #debug(f'State: {states_copy}')
        player = vboard.current_player()

        expand = True
        for t in range(1, self.max_moves + 1):
            legal = vboard.legal_moves()
            # debug(f'All legal Move: {legal}')
            if not legal:
                break
            moves_states = [(p, vboard.next_state(p)) for p in legal]

            if all(plays.get((player, S)) for p, S in moves_states):
                # If we have stats on all of the legal moves here, use them.
                d = [plays[(player, S)] for p, S in moves_states]
                debug(f'Debug: {d}')
                # debug(f' moves_states: {moves_states}')
                log_total = math.log(
                    sum(plays[(player, S)] for p, S in moves_states))
                value, move, state = max(
                    ((wins[(player, S)] / plays[(player, S)]) +
                     self.C * math.sqrt(log_total / plays[(player, S)]), p, S)
                    for p, S in moves_states
                )
            else:
                # Otherwise, just make an arbitrary decision.
                move, state = random.choice(moves_states)
            vboard.play(move)
            #debug(f'Player: {player} Move: {move}')

            # `player` here and below refers to the player
            # who moved into that particular state.
            if expand and (player, state) not in plays:
                expand = False
                plays[(player, state)] = 0
                wins[(player, state)] = 0
                if t > self.max_depth:
                    self.max_depth = t

            visited_states.add((player, state))

            winner = vboard.winner()
            if not winner == -1:
                debug(f'winner: {winner}')
                #vboard.print()
                break

            player = vboard.current_player()

        for player, state in visited_states:
            if (player, state) not in plays:
                continue
            plays[(player, state)] += 1
            if player == winner:
                wins[(player, state)] += 1


# game loop
board = Board9()
mcts = MCTS(board)
while True:
    opponent_size, opponent_col = [int(i) for i in input().split()]
    debug(f'opponent_size: {opponent_size } opponent_col:{opponent_col}')
    board.play((opponent_size, opponent_col)) if not opponent_size == -1 else None
    valid_action_count = int(input())
    board.clear_legal_moves()
    for i in range(valid_action_count):
        size, col = [int(j) for j in input().split()]
        # debug(f'size:{size}, col:{col}')
        board.add_legal_move((size, col))

    # Write an action using print
    # To debug: print("Debug messages...", file=sys.stderr)
    x, y = move = mcts.get_play()
    board.play(move)
    mcts.update_param(time=80, max_moves=200) if opponent_size == -1 else None
    print(f"{x} {y}")

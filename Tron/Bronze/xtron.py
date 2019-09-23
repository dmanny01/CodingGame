import sys
import math, datetime
from queue import Queue

def debug(*args, **kwargs):
	pass
	#print(*args, **kwargs, file=sys.stderr)
moves = {'UP':(-1, 0), 'DOWN':(1, 0), 'LEFT':(0, -1), 'RIGHT':(0, 1)}
game = None
players = None
hero = None
MIN, MAX = float('-inf'), float('inf')
width, height = 30, 20

class Pos:
	def __init__(self, i, j):
		self.i = i
		self.j = j

	def __repr__(self):
		return f'{self.i}, {self.j}'

	def __iter__(self):
		return iter([self.i, self.j])

class Player:
	def __init__(self, id):
		self.id = id
		self.pos = None
		self.pos_history = list()
		self.moves_history = list()
		self.score = 0

	def _fill(self, pos):
		#debug(f'Player:{self.id} fill @ {pos}')
		self.pos_history.append(self.pos)
		self.pos = pos
		game.fill_cell(self.id, *pos)

	def _undo_fill(self):
		#debug(f'Player:{self.id} undo @ {self.pos}')
		game.clear_cell(*self.pos)
		self.pos = self.pos_history.pop()


class Game:
	def __init__(self, n_players, *args, **kwargs):
		self.grid = [[-1 for i in range(30)] for j in range(20)]
		self.n = n_players
		self.calculation_time = datetime.timedelta(milliseconds=90)
		self.max_moves = kwargs.get('max_moves', 100)
		self.begin = None
		self.scores = [0] * n_players

	def fill_cell(self, id, i, j):
		self.grid[i][j] = id
		self.scores[id] += 1

	def clear_cell(self, i, j):
		id = self.grid[i][j]
		self.grid[i][j] = -1
		self.scores[id] -= 1

	def is_free(self, pos):
		i,j = pos
		#debug(f'is_free| i:{i} j:{j}')
		if 0 <= i < 20 and 0 <= j < 30:
			return self.grid[i][j] == -1
		return False

	def print_grid(self):
		for x, col in enumerate(self.grid):
			for y, val in enumerate(col):
				if val != -1:
					debug(f'|{val}', end='')
				else:
					debug(f'|F', end='')
			debug('\n')

	def bfs(self, v_scores):
		neighbours = [(0, -1), (0, 1), (-1, 0), (1, 0)]
		visited = set()
		q = Queue()
		for player in players:
			visited.add((player.pos.i, player.pos.j))
			q.put(((player.pos.i, player.pos.j), 0, player.id))
			v_scores[player.id] += 1
		while q.qsize():
			(i,j), dist, id = q.get()
			#debug(f'bfs node: {(i,j)}')
			for di, dj in neighbours:
				if 0 <= i + di < height and 0 <= j + dj < width and not (i + di, j + dj) in visited and self.grid[i + di][j + dj] == -1:
					#debug(f'bfs child: {i + di, j + dj}')
					v_scores[id] += 1
					visited.add((i + di, j + dj))
					q.put(((i + di, j + dj), dist+1, id))

	def voronoi(self):
		v_scores = self.scores.copy()
		self.bfs(v_scores)
		#debug(f'v_scores: {v_scores}')

		total = sum(v_scores)
		scores = [0] * len(players)
		for player in players:
			t = v_scores[player.id]
			scores[player.id] =  t* 1000 - (total - t)*1000
		return scores

	def min_max_simulation(self, depth, initial_depth, id):
		if depth == 0:
			return self.voronoi()

		best_score, best_move, scores = MIN, None, None
		for key, (di, dj) in moves.items():
			te = datetime.datetime.utcnow() - self.begin
			if te > self.calculation_time:
				debug(f'Breaking out|time elapsed: {te}ms')
				break
			player = players[id]
			i, j = player.pos
			next_pos = Pos(i + di, j + dj)
			if 0 <= i + di < height and 0 <= j + dj < width and self.grid[i + di][j + dj] == -1:
				player._fill(next_pos)
				scores = self.min_max_simulation(depth-1, initial_depth, (id+1)%self.n)  # next player
				#debug(f'{depth}: {key} {i,j}->{i + di,j + dj} score => {scores}')
				if scores[id] > best_score:
					best_score, best_move = scores[id], key
				player._undo_fill()
		if best_score == MIN and not depth == 0:
			scores = self.voronoi()
		return (best_score, best_move) if id == hero.id and depth == initial_depth else scores

	def move(self):
		debug('Move')
		#self.begin = datetime.datetime.utcnow()
		best_score, best_move = MIN, None
		for depth in range(2, self.max_moves):
			te = datetime.datetime.utcnow() - self.begin
			if te > self.calculation_time:
				debug(f'Breaking out|time elapsed: {te}ms')
				break
			else:
				debug(f'Depth:{depth} time elapsed: {te}ms')
				score, move = self.min_max_simulation(depth, depth, hero.id)
				if score > best_score:
					best_score = score; best_move = move

		if best_move:
			debug(f'found best move: {best_move}')
			pos, best_move = Pos(*moves[best_move]), best_move
		elif hero.moves_history:
			debug(f'old best move: {best_move}')
			pos, best_move = Pos(*moves[hero.moves_history[-1]]), hero.moves_history[-1]
			i, j = hero.pos.i + pos.i, hero.pos.j + pos.j
			if not (0 <= i < height and 0 <= j < width and self.grid[i][j]) == -1:
				i, j = hero.pos
				for key, (di, dj) in moves.items():
					if 0 <= i + di < height and 0 <= j + dj < width and self.grid[i+di][j+dj] == -1:
						pos, best_move = Pos(i+di, j+dj), key
		else:
			debug(f'default move: {best_move}')
			pos, best_move = Pos(*moves['UP']), 'UP'
			i, j = hero.pos.i + pos.i, hero.pos.j + pos.j
			if not (0 <= i < height and 0 <= j < width and self.grid[i][j] == -1):
				i, j = hero.pos
				for key, (di, dj) in moves.items():
					if 0 <= i + di < height and 0 <= j + dj < width and self.grid[i+di][j+dj] == -1:
						pos, best_move = Pos(i+di, j+dj), key
		next_pos = hero.pos.i + pos.i, hero.pos.j + pos.j
		# hero._fill(next_pos)
		hero.moves_history.append(best_move)
		print(best_move)

# game loop
while True:
	# n: total number of players (2 to 4).
	# p: your player number (0 to 3).
	start = datetime.datetime.utcnow()
	n, p = [int(i) for i in input().split()]
	#debug(f'#player:{n}, my_id: {p}')
	if not game:
		game = Game(n)
		players = [Player(i) for i in range(n)]
		hero = players[p]
	game.begin = start
	for i in range(n):
		te = datetime.datetime.utcnow() - start
		x0, y0, x1, y1 = [int(j) for j in input().split()] # Note x in col y in row
		debug(f'{i}: Initial {y0} {x0} | Final {y1} {x1} time: {te}')
		players[i]._fill(Pos(y1, x1))
	# game.print_grid()
	game.move()

import sys
import math
from collections import namedtuple
from queue import Queue
import datetime
import copy

sys.maxsize = 1000

# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.
def debug(*args, **kwargs):
	pass
	#print(*args, **kwargs, file=sys.stderr)

width, height, my_id = [int(i) for i in input().split()]
# debug(f'width: {width} height: {height} my_id:{my_id}')

grid = None
items = None
neighbours = [(-1, 0), (1, 0), (0, -1), (0, 1)]
positions = [None] * 4
n_bombs = 0
ranges = [None] * 4
Cell = namedtuple('Cell', 'val owner time bomb_range')

class DPCell:
	def __init__(self, val, dist, min_bombing_duration, parent):
		self.val = val
		self.dist = dist
		self.parent = parent
		self.min_bombing_duration = min_bombing_duration

	def __iter__(self):
		return iter([self.val, self.dist, self.parent, self.min_bombing_duration])

	def __repr__(self):
		return f'{self.val} {self.dist} {self.parent} {self.min_bombing_duration}'

class GameSimulation:
	def __init__(self):
		self.best_positions_bombs = None
		self.best_positions_points = None
		self.last_pos = None
		self.safe_positions = list()
		self.dp = None  # Simulation grid
		self.calculation_time = datetime.timedelta(milliseconds=80)
		self.reserved_time = datetime.timedelta(milliseconds=15)
		self.begin = None
		self.bp = None
		self.for_bombing = False

	@staticmethod
	def add_reacability(pos, _dp):
		i, j = pos
		dp = copy.deepcopy(_dp)
		visited = set()
		dp[i][j].dist, dp[i][j].parent = 0, (None, None)
		visited.add((i, j))
		safe_pos = list()
		safe_pos.append((i, j)) if dp[i][j].min_bombing_duration == sys.maxsize else None
		q = Queue()
		q.put((dp[i][j], (i, j)))

		while q.qsize():
			(_, dist,_, _), (i, j) = q.get()
			for di, dj in neighbours:
				# and not dp[i + di][j + dj].min_bombing_duration <= 2\
				if 0 <= i + di < height and 0 <= j + dj < width and not (i + di, j + dj) in visited and (
						grid[i + di][j + dj].val == -1  # Empty\
						or (grid[i + di][j + dj].val > 0 and items[i + di][
					j + dj] > 0)):
					dp[i + di][j + dj].dist, dp[i + di][j + dj].parent = dist + 1, (i, j)
					visited.add((i + di, j + dj))
					q.put((dp[i + di][j + dj], (i + di, j + dj)))
					safe_pos.append((i + di, j + dj)) if dp[i + di][j + dj].min_bombing_duration == sys.maxsize else None
		return safe_pos, dp

	@staticmethod
	def if_safe_path(start, end, dp):
		temp = end
		while not temp == start:
			i, j = temp
			debug(f'node:{i}{j}, timer: {dp[i][j].min_bombing_duration} dist:{dp[i][j].dist}')
			if dp[i][j].dist-1 <= dp[i][j].min_bombing_duration <= dp[i][j].dist+1:
				return False
			temp = dp[i][j].parent
		return True

	def init_board(self, pos):
		self.dp.clear() if self.dp else None
		self.safe_positions.clear() if self.safe_positions else None
		dp = self.dp = [[DPCell(0, sys.maxsize, sys.maxsize, None) for _ in range(width)] for _ in range(height)]
		for i in range(len(grid)):  # if bomb placed here
			for j in range(len(grid[0])):
				if grid[i][j].val == 3:
					_range = grid[i][j].bomb_range
					dp[i][j].val = 0
					dp[i][j].min_bombing_duration = min(dp[i][j].min_bombing_duration, grid[i][j].time)
					for x in range(max(i-1, 0), max(i - (_range), -1), -1):  # up
						if grid[x][j].val == -1:
							dp[x][j].val = 0
							dp[x][j].min_bombing_duration = min(dp[x][j].min_bombing_duration, dp[i][j].min_bombing_duration)
							continue
						else:
							dp[x][j].min_bombing_duration = min(dp[x][j].min_bombing_duration, dp[i][j].min_bombing_duration)
							break
					for x in range(min(i+1, height), min(i + (_range), height)):  # down
						if grid[x][j].val == -1:
							dp[x][j].val = 0
							dp[x][j].min_bombing_duration = min(dp[x][j].min_bombing_duration, dp[i][j].min_bombing_duration)
							continue
						else:
							dp[x][j].min_bombing_duration = min(dp[x][j].min_bombing_duration, dp[i][j].min_bombing_duration)
							break
					for y in range(max(j-1, 0), max(j - (_range), -1), -1):  # left
						if grid[i][y].val == -1:
							dp[i][y].val = 0
							dp[i][y].min_bombing_duration = min(dp[i][y].min_bombing_duration, dp[i][j].min_bombing_duration)
						else:
							dp[i][y].min_bombing_duration = min(dp[i][y].min_bombing_duration, dp[i][j].min_bombing_duration)
							break
					for y in range(min(j+1, width), min(j + (_range), width)):  # right
						if grid[i][y].val == -1:
							dp[i][y].val = 0
							dp[i][y].min_bombing_duration = min(dp[i][y].min_bombing_duration, dp[i][j].min_bombing_duration)
						else:
							dp[i][y].min_bombing_duration = min(dp[i][y].min_bombing_duration, dp[i][j].min_bombing_duration)
							break

				if grid[i][j].val == -1:
					_range = ranges[my_id]
					for x in range(max(i-1, 0), max(i - (_range), -1), -1):  # up
						if grid[x][j].val == -2 or items[x][j] or not dp[x][j].min_bombing_duration == sys.maxsize:
							break
						if grid[x][j].val > 0 and dp[x][j].min_bombing_duration == sys.maxsize:
							dp[i][j].val += 1
							break
					for x in range(min(i+1, height), min(i + (_range), height)):  # down
						if grid[x][j].val == -2 or items[x][j] or not dp[x][j].min_bombing_duration == sys.maxsize:
							break
						if grid[x][j].val > 0 and dp[x][j].min_bombing_duration == sys.maxsize:
							dp[i][j].val += 1
							break
					for y in range(max(j-1, 0), max(j - (_range), -1), -1):  # left
						if grid[i][y].val == -2 or items[i][y] or not dp[i][y].min_bombing_duration == sys.maxsize:
							break
						if grid[i][y].val > -1 and dp[i][y].min_bombing_duration == sys.maxsize:
							dp[i][j].val += 1
							break
					for y in range(min(j+1, width), min(j + (_range), width)):  # right
						if grid[i][y].val == -2 or items[i][y] or not dp[i][y].min_bombing_duration == sys.maxsize:
							break
						if grid[i][y].val > -1 and dp[i][y].min_bombing_duration == sys.maxsize:
							dp[i][j].val += 1
							break

		self.safe_positions, self.dp = self.add_reacability(pos, self.dp)

	def evaluate_game(self, pos):
		self.init_board(pos)  # static without bombs
		# self.add_bombs(pos)
		dp = self.dp
		self.best_positions_bombs = sorted(
			[(dp[i][j].val, -1 * dp[i][j].dist, (i, j)) for j in range(len(dp[0])) for i in range(len(dp)) if
			 dp[i][j].min_bombing_duration >= sys.maxsize and dp[i][j].dist < 50 and dp[i][j].val > 0],
			key=lambda elem: (elem[0], elem[1]), reverse=True)
		debug(f'best_positions_bombs: {self.best_positions_bombs}')

		self.best_positions_points = sorted(
			[(abs(pos[0] - i) + abs(pos[1] - j), (i, j)) for j in range(len(items[0])) for i in range(len(items)) if
			 items[i][j] and not dp[i][j].min_bombing_duration == dp[i][j].dist and dp[i][j].dist < 50])
		debug(f'best_positions_points: {self.best_positions_points}')

		debug(f'safe_positions: {self.safe_positions}')

	def try_bomb_at(self, plant_bomb_at):
		curr_pos = positions[my_id]
		dp = copy.deepcopy(self.dp)
		debug(f'Try Bomb at {plant_bomb_at}')
		i, j = plant_bomb_at
		if not self.if_safe_path(curr_pos, plant_bomb_at, self.dp):
			return None

		temp = copy.deepcopy(grid[i][j])
		grid[i][j] = Cell(3, my_id, 8, ranges[my_id])  # simulation
		_range = grid[i][j].bomb_range

		for x in range(max(i - (_range - 1), 0), min(i + (_range), height)):
			if grid[x][j].val == -2 or items[x][j]:
				dp[x][j].min_bombing_duration = min(dp[x][j].min_bombing_duration, grid[i][j].time)
				break
			dp[x][j].val = 0
			dp[x][j].min_bombing_duration = min(dp[x][j].min_bombing_duration, grid[i][j].time)
		for y in range(max(j - (_range - 1), 0), min(j + (_range), width)):
			if grid[i][y].val == -2 or items[i][y]:
				dp[i][y].min_bombing_duration = min(dp[i][y].min_bombing_duration, grid[i][j].time)
				break
			dp[i][y].val = 0
			dp[i][y].min_bombing_duration = min(dp[i][y].min_bombing_duration, grid[i][j].time)

		safe_positions, dp = self.add_reacability(plant_bomb_at, dp)
		debug(f'safe_positions:{safe_positions}')
		if not safe_positions:
			grid[i][j] = temp  # restore
			return None
		self.safe_positions, self.dp = safe_positions, dp
		return plant_bomb_at

	def try_pos(self, next_pos):
		curr_pos = positions[my_id]
		dp = copy.deepcopy(self.dp)
		debug(f'Try next pos {next_pos}')
		i, j = next_pos
		if not self.if_safe_path(curr_pos, next_pos, self.dp):
			return None
		safe_positions, dp = self.add_reacability(next_pos, dp)
		debug(f'safe_positions:{safe_positions}')
		if not safe_positions:
			return None
		self.safe_positions, self.dp = safe_positions, dp
		return next_pos

	def dist(self, end, start):
		i, j = end
		return self.dp[i][j].dist

	def next_pos(self, pos):
		self.evaluate_game(pos)

		bp , for_bombing = None, False
		while not bp:
			if datetime.datetime.utcnow() - self.begin > self.calculation_time:
				debug(f'Timing out: T = {datetime.datetime.utcnow() - self.begin}')
				break
			bp1, bp2 = None, None
			if n_bombs and self.best_positions_bombs:
				_, _, bp1 = self.best_positions_bombs.pop(0)
			if self.best_positions_points:
				_, bp2 = self.best_positions_points.pop(0)
			if bp1 and bp2:
				if self.dist(bp1, pos) < self.dist(bp2, pos):
					bp = self.try_bomb_at(bp1)
					for_bombing = True if bp else False
				else:
					bp = self.try_pos(bp2)
			elif bp1:
				bp = self.try_bomb_at(bp1)
				for_bombing = True if bp else False
			elif bp2:
				bp = self.try_pos(bp2)

		# Safety if no pos found		
		while not bp and self.safe_positions:
			if datetime.datetime.utcnow() - self.begin > self.calculation_time + self.reserved_time:
				debug(f'Timing out: T = {datetime.datetime.utcnow() - self.begin}')
				break
			bp3 = self.safe_positions.pop(0)
			bp = self.try_pos(bp3)

		debug(f'bp:{bp} for_bombing:{for_bombing}')
		return bp, for_bombing

	def play(self, pos):
		self.begin = datetime.datetime.utcnow()
		bp, for_bombing = self.next_pos(pos)
		if bp:
			debug(f'bp:{bp} pos: {pos}')
			if bp == pos and for_bombing:
				print(f"BOMB {bp[1]} {bp[0]}")
			else:
				i, j = curr_pos
				next_pos_up = i, max(j - 1, 0)
				next_pos_down = i, min(j + 1, height)
				next_pos_left = max(0, i - 1), j
				next_pos_right = min(width, i + 1), j

				for di, dj in neighbours:
					if 0 <= i + di < height and 0 <= j + dj < width and self.dp[i + di][
						j + dj].min_bombing_duration <= 2:
						break
				else:
					print(f'MOVE {bp[1]} {bp[0]}')
					return
				if self.dp[i][j].min_bombing_duration <= 2 and self.safe_positions:
					debug('Danger: move to safety')
					bp = self.safe_positions.pop(0)
					print(f'MOVE {bp[1]} {bp[0]}')
					return
				debug('Stay')
				print(f'MOVE {pos[1]} {pos[0]}')
			self.last_pos = pos
		else:
			debug(f'No moves')
			print(f'MOVE {pos[1]} {pos[0]}')

gp = GameSimulation()
# game loop
while True:
	grid = [[-1 for _ in range(width)] for _ in range(height)]
	items = [[0 for _ in range(width)] for _ in range(height)]
	for i in range(height):
		row = input()
		# debug(f'{row}')
		for col, val in enumerate(list(row)):
			if val == '.':
				grid[i][col] = Cell(-1, None, sys.maxsize, None)
			elif val == 'x' or val == 'X':
				grid[i][col] = Cell(-2, None, sys.maxsize, None)
			else:
				grid[i][col] = Cell(int(val), None, sys.maxsize, None)
	entities = int(input())
	# debug(f'entities: {entities}')
	for i in range(entities):
		entity_type, owner, x, y, param_1, param_2 = [int(j) for j in input().split()]
		# debug(f'entity_type:{entity_type}, owner:{owner}, x:{x}, y:{y}, param_1:{param_1}, param_2:{param_2}')
		if entity_type == 0:  # Player
			positions[owner] = y, x
			if owner == my_id:
				n_bombs = param_1
				ranges[my_id] = param_2
		elif entity_type == 1:
			grid[y][x] = Cell(3, owner, param_1, param_2)  # Bomb
		else:  # items
			items[y][x] = param_1  # val 1 or 2
			debug(f'items: {items[y][x]}, {(y,x)}')

	curr_pos = positions[my_id]
	gp.play(curr_pos)

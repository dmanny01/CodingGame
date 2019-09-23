import sys
import math

# Grab Snaffles and try to throw them through the opponent's goal!
# Move towards a Snaffle and use your team id to determine where you need to throw it.
def debug(*args, **kwargs):
	print(*args, **kwargs, file=sys.stderr)

my_team_id = int(input())  # if 0 you need to score on the right of the map, if 1 you need to score on the left
my_players = [None] * 2
wizards = list()
opponent_wizards = [None] * 2
snaffles = list()
goals = [(0, 3750), (16000, 3750)]
center = 16000//2 , 7500//2
poles = [(0,5750),(16000,5750)]

class Wizard:
	def __init__(self, id, x, y, vx, vy, state):
		self.id = id
		self.pos = x, y
		self.velocity = vx, vy
		self.state = state
		self.assigned = None
		self.thrust = 100
		self.power = 500

	def update(self, x, y, vx, vy, state):
		self.pos = x, y
		self.velocity = vx, vy
		self.state = state

	def assign_snaffle(self, snaffle):
		self.assigned = snaffle
		debug(f'Assigned {self.id} => {self.assigned}')

	def clear(self):
		self.assigned = None
		self.state = 0

	def calculate_thrust(self):
		pvx, pvy = self.velocity[0], self.velocity[1]
		svx, svy = self.assigned.velocity[0], self.assigned.velocity[1]
		thx = (svx - pvx) * 2
		thy = (svy - pvy) * 2
		thrust = math.sqrt(thx**2 + thy**2)
		if thrust:
			self.thrust = int(min(150, thrust))

	def play(self):
		if self.state == 0:
			if self.assigned:
				self.calculate_thrust()
				debug(f'{self.id}: {self.assigned}')
				print(f'MOVE {self.assigned.pos[0]} {self.assigned.pos[1]} {self.thrust}')
			else:
				debug('Move to opponent')
				print(f'MOVE {poles[my_team_id^1][0]} {poles[my_team_id^1][1]} {self.thrust}')
		else:
			debug(f'{self.id} Throw')
			print(f'THROW {goals[my_team_id^1][0]} {goals[my_team_id^1][1]} {self.power}')

class Snaffle:
	def __init__(self, id, x, y, vx, vy, state):
		self.id = id
		self.pos = x, y
		self.velocity = 0.75*vx, 0.75*vy
		self.state = state

	def update(self, x, y, vx, vy, state):
		self.pos = x, y
		self.velocity = 0.75*vx, 0.75*vy
		self.state = state

	def clear(self):
		self.state = 0

	def __repr__(self):
		return f'{self.id}'

def dist(x, y):
	return math.sqrt((x[0]-y[0])**2 + (x[1]-y[1])**2)

def evaluate():
	for wizard in wizards:
		if wizard.state == 0:
			t = sorted([snaffle for snaffle in snaffles if snaffle.state == 0], key= lambda snaffle: (dist(goals[my_team_id], wizard.pos), dist(wizard.pos, snaffle.pos))) 
			if t:
				debug(f'Eval {wizard.id} => {t}')
				nearest = t[0]
				nearest.state = 1
				wizard.assign_snaffle(nearest)

# game loop
while True:
	my_score, my_magic = [int(i) for i in input().split()]
	opponent_score, opponent_magic = [int(i) for i in input().split()]
	entities = int(input())  # number of entities still in game
	snaffles.clear()
	wizards.clear()

	for i in range(entities):
		# entity_id: entity identifier
		# entity_type: "WIZARD", "OPPONENT_WIZARD" or "SNAFFLE" (or "BLUDGER" after first league)
		# x: position
		# y: position
		# vx: velocity
		# vy: velocity
		# state: 1 if the wizard is holding a Snaffle, 0 otherwise
		entity_id, entity_type, x, y, vx, vy, state = input().split()
		entity_id = int(entity_id)
		x = int(x)
		y = int(y)
		vx = int(vx)
		vy = int(vy)
		state = int(state)
		if entity_type == 'WIZARD':
			wizards.append(Wizard(entity_id, x, y, vx, vy, state))
		if entity_type == 'SNAFFLE':
			snaffles.append(Snaffle(entity_id, x, y, vx, vy, state))
	evaluate()
	for i in range(2):
		wizards[i].play()


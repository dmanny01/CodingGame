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
bludgers = list()
goals = [(0, 3750), (16000, 3750)]
center = 16000//2 , 7500//2
poles_y = (2200, 5200) # normalized with radius
my_score, my_magic = 0, 0
CODE_GREEN, CODE_RED = 1, 2
code = 1

class GoalPost:
	def __init__(self, x, y):
		self.pos = x, y
		self.occupied = False

goalposts = [GoalPost(200, 3750), GoalPost(14000, 3750)]


class Wizard:
	def __init__(self, id, x, y, vx, vy, state):
		self.id = id
		self.pos = x, y
		self.velocity = vx, vy
		self.state = state
		self.assigned = None
		self.thrust = 100
		self.power = 500
		self.next_pos = None

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
		t1 = sorted([(snaffle, dist(self.pos, snaffle.pos)) for snaffle in snaffles if not snaffle.assigned and (goals[my_team_id^1][0]-self.pos[0]) - (goals[my_team_id^1][0]-snaffle.pos[0]) < 0], key=lambda elem :dist(self.pos, elem[0].pos))
		t2 = sorted([(snaffle, dist(self.pos, snaffle.pos)) for snaffle in snaffles if my_team_id and abs(snaffle.pos[0]-goals[my_team_id][0]) < 400 and dist(snaffle.pos, self.pos) < 8000], key=lambda elem:dist(self.pos, elem[0].pos)) # Defence
		if self.state == 0:
			if self.assigned:
				if (goals[my_team_id^1][0]-self.pos[0]) - (goals[my_team_id^1][0]-self.assigned.pos[0]) < 0 and my_magic >= 20:
					print(f'ACCIO {self.assigned.id}')
					return
				self.calculate_thrust()
				debug(f'{self.id}: {self.assigned}')
				print(f'MOVE {self.assigned.pos[0]} {self.assigned.pos[1]} {self.thrust}')
			else:
				t = None
				if t1 and t2:
					t = t1[0][0] if t1[0][1] < t2[0][1] else t2[0][0]
				elif t1:
					t = t1[0][0]
				elif t2:
					t = t2[0][0]
				if t and my_magic > 15:
					print(f'ACCIO {t.id}')
				else:
					if not goalposts[my_team_id].occupied:
						debug('Move to home goalpost')
						goalposts[my_team_id].occupied = True
						print(f'MOVE {goalposts[my_team_id].pos[0]} {goalposts[my_team_id].pos[1]} {self.thrust}')
					else:
						debug('Move to home center')
						print(f'MOVE {center[0]} {center[1]} {self.thrust}')
		else:
			if not wizards[self.id^1].assigned and dist(self.pos, goals[my_team_id^1]) > dist(wizards[self.id^1].pos, goals[my_team_id^1]):
				debug(f'pass to {self.id^1}')
				x, y = wizards[self.id^1].pos
			else:
				debug(f'{self.id} Throw')
				x, y = goals[my_team_id^1][0], goals[my_team_id^1][1]
				if abs(self.pos[0] - goals[my_team_id^1][0]) < 500:
					if poles_y[0] < self.pos[0] < poles_y[1]:
						y = self.pos[0]
					else:
						y = poles_y[0] if abs(poles_y[0] - self.pos[0]) < abs(poles_y[1] - self.pos[0]) else poles_y[1]
			print(f'THROW {x} {y} {self.power}')

class Snaffle:
	def __init__(self, id, x, y, vx, vy, state):
		self.id = id
		self.pos = x, y
		self.velocity = 0.75*vx, 0.75*vy
		self.state = state
		self.next_pos = None
		self.assigned = None

	def update(self, x, y, vx, vy, state):
		self.pos = x, y
		self.velocity = 0.75*vx, 0.75*vy
		self.state = state

	def __repr__(self):
		return f'{self.id}'

class Bludger:
	def __init__(self, id, x, y, vx, vy, state):
		self.id = id
		self.pos = x, y
		self.velocity = 0.9*vx, 0.9*vy
		self.state = state
		self.thrust = 1000
		self.next_pos = None

def dist(x, y):
	return math.sqrt((x[0]-y[0])**2 + (x[1]-y[1])**2)

def evaluate():
	for snaffle in snaffles:
		snaffle.next_pos = snaffle.pos[0] + snaffle.velocity[0], snaffle.pos[1]+snaffle.velocity[1]

	for ow in opponent_wizards:
		ow.next_pos = ow.pos[0] + ow.velocity[0], ow.pos[1] + ow.velocity[1]

	for bludger in bludgers:
		ow.next_pos = ow.pos[0] + ow.velocity[0], ow.pos[1] + ow.velocity[1]

	ns = [snaffle.state for snaffle in snaffles].count(0)
	if ns > 3:
		code = CODE_GREEN
	else:
		code = CODE_RED

	if code == CODE_GREEN  or code == CODE_RED:
		for wizard in wizards:
			if wizard.state == 0:
				t = sorted([snaffle for snaffle in snaffles if not snaffle.state and not snaffle.assigned], key= lambda snaffle: (dist(wizard.pos, snaffle.next_pos) + 10*(dist(goals[my_team_id^1], wizard.pos))))
				if t :
					debug(f'Eval {wizard.id} => {t}')
					nearest = t[0]
					nearest.assigned = 1
					wizard.assign_snaffle(nearest)
		if wizards[0].assigned and wizards[1].assigned:
			if dist(wizards[0].assigned.pos, wizards[1].pos) - dist(wizards[0].assigned.pos, wizards[0].pos) < 0 and dist(wizards[1].assigned.pos, wizards[0].pos) - dist(wizards[1].assigned.pos, wizards[1].pos) < 0:
				wizards[0].assigned, wizards[1].assigned = wizards[1].assigned, wizards[0].assigned 


# game loop
while True:
	my_score, my_magic = [int(i) for i in input().split()]
	opponent_score, opponent_magic = [int(i) for i in input().split()]
	entities = int(input())  # number of entities still in game
	snaffles.clear()
	wizards.clear()
	opponent_wizards.clear()
	bludgers.clear()
	code = 1

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
		if entity_type == 'OPPONENT_WIZARD':
			opponent_wizards.append(Wizard(entity_id, x, y, vx, vy, state))
		if entity_type == 'BLUDGER':
			bludgers.append(Bludger(entity_id, x, y, vx, vy, state))

	evaluate()
	for i in range(2):
		wizards[i].play()


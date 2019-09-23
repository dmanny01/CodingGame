import sys
import math
from enum import Enum
import abc
import bisect
from collections import defaultdict
import random
import numpy as np

def debug(*args, **kwargs):
    print(*args, **kwargs, file=sys.stderr)

# Send your busters out into the fog to trap ghosts and bring them home!
busters_per_player = int(input())  # the amount of busters you control
ghost_count = int(input())  # the amount of ghosts on the map
my_team_id = int(input())  # if this is 0, your base is on the top left of the map, if it is one, on the bottom right
debug(f'busters_per_player: {busters_per_player}, ghost_count: {ghost_count} my_team_id: {my_team_id}')
# code Manish
busters = dict()
ghosts = dict()
captured_ghost_id = list()
assignment_map = defaultdict(list)

class State(metaclass=abc.ABCMeta):
    states = Enum('states', 'Free Assigned Ready Captured')

    def __init__(self):
        self._state = self.states.Free

    @abc.abstractmethod
    def move(self):
        pass

def distance(pos1, pos2):
    result = max(abs(pos1[0] - pos2[0]), abs(pos1[1] - pos2[1]))
    return result

def reassign(busters, ghosts):
    assignment_map.clear()
    for key, value in ghosts.items():
        assignment_map[key] = sorted(list(busters.keys()),
                                     key=lambda buster_key: distance(busters[buster_key].pos, value.pos))

    for ghost_id, buster_ids in assignment_map.items():
        ghost = ghosts[ghost_id]
        debug(f'Assignment=>Ghost: {ghost_id} is_free: {ghost._state}, Busters: {buster_ids}')
        if ghost._state == Ghost.states.Free:
            for buster_id in buster_ids:
                buster = busters.get(buster_id)
                if buster._state == State.states.Free:
                    buster.assign(ghost_id)
                    ghost.free = False
                    break

def fallback_assign(buster, ghost_id):
    ghost = ghosts.get(ghost_id)
    if ghost and ghost._state == Ghost.states.Free:
        buster.assign(ghost_id)
        return True
    return False

class Ghost:
    states = Enum('states', 'Free Captured')

    def __init__(self, id, entity_type, x, y, state, value):
        self.id = id
        self.team = entity_type
        self.pos = x, y
        self.state = state
        self.value = value
        self._state = self.states.Free

    def update(self, x, y, state, value):
        if not self.is_alive():
            return
        self.pos = x, y
        self.state = state
        self.value = value
        self._state = self.states.Free

    def kill(self):
        self._state = self.states.Captured

    def is_alive(self):
        return self._state == self.states.Free

class Buster(State):
    def __init__(self, id, entity_type, x, y, state, value):
        super().__init__()
        self.id = id
        self.team = entity_type
        self.pos = x, y
        self.state = state
        self.value = value
        self.target_ghost_id = None
        self.flip = id
        if state:
            self._state = State.states.Captured
            captured_ghost_id.append(value)
        if self.team == 0:
            self.base = (0, 0)
        else:
            self.base = (16000, 9000)

    def update(self, x, y, state, value):
        self.pos = x, y
        self.state = state
        self.value = value
        self._state = State.states.Free
        if state:
            self._state = State.states.Captured
            self.target_ghost_id = value

    def assign(self, ghost_id):
        self._state = State.states.Assigned
        self.target_ghost_id = ghost_id
        debug(f'Buster {self.id} assigned ghost {self.target_ghost_id}')

    def move_to_base(self):
        d = distance(self.pos, self.base)
        debug(f'Move to base: {d}')
        if d > 1600:
            print(f'MOVE {self.base[0]} {self.base[1]}')
            return False
        return True

    def move_to_target(self):
        pos = ghosts[self.target_ghost_id].pos
        d = distance(self.pos, pos)
        debug(f'Move to target ghost_id:{self.target_ghost_id} distance: {d}')
        if 1500 < d:
            print(f'MOVE {pos[0]} {pos[1]}')
            return False
        elif d < 900:
            pos = abs(950 - pos[0]) + pos[0], pos[1]
            print(f'MOVE {pos[0]} {pos[1]}')
            return False
        return True

    def bust_if_allowed(self):
        target_pos = ghosts[self.target_ghost_id].pos
        d = distance(self.pos, target_pos)
        debug(f'Bust if allowed {d}')
        if 1760 > d > 900:
            print(f'BUST {self.target_ghost_id}')
            return True
        return False

    def move_random(self):
        # pos = random.randrange(-8000, 8000) * 2 + 8000, random.randrange(-4500, 4500) * 2 + 4500
        # pos = int(random.normalvariate(8000, 16000)) , int(random.normalvariate(4500, 9000))
        if self.base == (16000, 9000):
            pos = random.randrange(self.pos[0], 0, -400), random.randrange(9000, 0, -400)
            '''
            distance_from_wall = distance((0,0), (self.pos[0],0))
            if distance_from_wall < 800:
                self.flip = 1^self.flip
            if self.flip & 1:
                pos = random.randrange(self.pos[0], 0, -400) , random.randrange(9000, 0, -400)
            else:
                pos = random.randrange(16000, 0, -400), random.randrange(self.pos[1], 0, -400)
            '''
            debug(f'Base[1] Random move: {pos}')
        else:
            pos = random.randrange(self.pos[0], 16000,400), random.randrange(0, 9000,400)
            # pos = self.pos[0] + int(random.gauss(8000,8000)), self.pos[1] + int(random.gauss(4500, 9000))
            '''
            distance_from_wall = distance((16000, 0), (self.pos[0], 0))
            if distance_from_wall < 800:
                self.flip = 1 ^ self.flip
            if self.flip & 1:
                pos = random.randrange(self.pos[0], 16000, 400), random.randrange(0, 9000, 400)
            else:
                pos = random.randrange(0, 16000, 400), random.randrange(self.pos[1], 9000, 400)
            '''
            debug(f'Base[0] Random move: {pos}')
        print(f'MOVE {pos[0]} {pos[1]}')

    def move(self):
        debug(f'Buster: {self.id} Current State: {self._state}')
        if self._state == State.states.Captured:
            at_base = self.move_to_base()
            if at_base:
                print(f'RELEASE')
                self._state = State.states.Free

        elif self._state == State.states.Ready:
            result = self.bust_if_allowed()
            if not result:
                if fallback_assign(self, self.target_ghost_id):
                    self._state = State.states.Assigned
                else:
                    self._state = State.states.Free
                debug(f'Not Busted, state: {self._state}')
                self.move()
            else:
                self._state = State.states.Captured

        elif self._state == State.states.Assigned:
            in_range = self.move_to_target()
            if in_range:
                debug('In range distance: ' + str(distance(self.pos, ghosts[self.target_ghost_id].pos)))
                self._state = State.states.Ready
                self.move()

        elif self._state == State.states.Free:
            self.move_random()

# game loop
while True:
    entities = int(input())  # the number of busters and ghosts visible to you
    ghosts.clear()
    for i in range(entities):
        # entity_id: buster id or ghost id
        # y: position of this buster / ghost
        # entity_type: the team id if it is a buster, -1 if it is a ghost.
        # state: For busters: 0=idle, 1=carrying a ghost.
        # value: For busters: Ghost id being carried. For ghosts: number of busters attempting to trap this ghost.
        entity_id, x, y, entity_type, state, value = [int(j) for j in input().split()]
        debug(i, ":", f'entity_id: {entity_id} x:{x} y:{y} entity_type:{entity_type} state:{state} value:{value}')
        if entity_type != -1:
            if not busters.get(entity_id):
                busters[entity_id] = Buster(entity_id, entity_type, x, y, state, value)
            else:
                busters[entity_id].update(x, y, state, value)
        else:
            if entity_id not in captured_ghost_id:
                ghosts[entity_id] = Ghost(entity_id, entity_type, x, y, state, value)

        reassign(busters, ghosts) if ghosts else None

    for i in range(busters_per_player):
        # Write an action using print
        # To debug: print("Debug messages...", file=sys.stderr)

        # MOVE x y | BUST id | RELEASE
        busters[i].move()
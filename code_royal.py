import sys
import math

# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.
def debug(*args, **kwargs):
    print(*args, **kwargs, file=sys.stderr)

cost = [80,100] #0 Knight, 1 Archer
KNIGHT = 0
ARCHER = 1
FRIENDLY = 0
ENEMY = 1

class Pos:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f'{self.x},{self.y}'

class Queen:
    def __init__(self, id, pos, health):
        self.id = id
        self.pos = pos
        self.health = health
        self.archer_site = list()
        self.knight_site = list()
        self.knight_creeps = list()
        self.archer_creeps = list()

    def __repr__(self):
        return f'id: {self.id} pos:{self.pos} health: {self.health}'

class Site:
    def __init__(self, id, pos , radius, type=None, owner=None):
        self.id = id
        self.pos = pos
        self.radius = radius
        self.type = None
        self.if_barrack = False
        self.owner = None
        self.snooze_timer = 100  # Big Num

    def update(self, ignore_1, ignore_2, structure_type, owner, param_1, param_2):
        self.if_barrack = False if structure_type == -1 else True
        self.type = param_2
        self.owner = owner
        self.snooze_timer = param_1

    def __repr__(self):
        return f'Id: {self.id} pos: {self.pos} type: {self.type} snooze_timer:{self.snooze_timer}'


class Creep:
    def __init__(self, type, owner, pos, health):
        self.type = type
        self.owner = owner
        self.pos = pos
        self.health = health

    def __repr__(self):
        return f'type: {self.type} owner:{self.owner} pos:{self.pos}'

class Game:
    def __init__(self, num_sites):
        self.queens = [None, None]
        self.num_sites = num_sites
        self.sites = [None for _ in range(num_sites)]
        self.creeps = list()
        self.hero = None

    def __str__(self):
        result = f'Queens: {self.queens}\n'
        for site in self.sites:
            result += f'Site: {site}\n'
        for creep in self.creeps:
            result += f'Creep: {creep}\n'
        result += f'Hero: {self.hero}'
        return result

    def clear(self):
        self.creeps.clear()
        for queen in self.queens:
            if queen:
                queen.archer_site.clear()
                queen.knight_site.clear()
                queen.knight_creeps.clear()
                queen.archer_creeps.clear()

    @staticmethod
    def dist(start, end):
        return math.sqrt((start.x-end.x)*(start.x-end.x) + (start.y-end.y)*(start.y-end.y))

    def min_distance_site(self, pos, free_sites):
        result, min_dist = None, sys.maxsize
        for site in free_sites:
            d = self.dist(pos, site.pos)
            if d < min_dist:
                min_dist = d
                result = site
        return result

    def next_triangle_point(self, pos1, pos2, free_sites):
        result, min_dist = None, sys.maxsize
        for site in free_sites:
            d1 = self.dist(pos1, site.pos); d2 = self.dist(pos2, site.pos)
            d = d1*d1 + d2*d2
            if d < min_dist:
                min_dist = d
                result = site
        return result

    def in_radius_of_archer(self, pos, r):
        min_x, max_x = max(pos.x-r, 0), min(pos.x+r, 1920)
        min_y, max_y = max(pos.y-r, 0), min(pos.y+y, 1000)
        result = list(filter(lambda e: min_x < e.pos.x < max_x and min_y < e.pos.y < max_y, self.queens[ENEMY].knight_creeps))
        return result

    def play_phase1(self):
        free_sites = sorted([site for site in self.sites if site.if_barrack == False], key=lambda site:self.dist(self.hero.pos, site.pos))
        if not self.hero.knight_site and free_sites:
            site = free_sites.pop(0)
            print(f'BUILD {site.id} BARRACKS-KNIGHT')
            return
        
        if free_sites and len(self.hero.archer_site) < 3 and gold > 80:
            if len(self.hero.archer_site) == 0:
                site = free_sites.pop(0)
                print(f'BUILD {site.id} BARRACKS-ARCHER')
                return
            if len(self.hero.archer_site) == 1:
                site = self.min_distance_site(self.hero.archer_site[0].pos, free_sites)
                if site:
                    print(f'BUILD {site.id} BARRACKS-ARCHER')
                    return
            if len(self.hero.archer_site) == 2:
                site = self.next_triangle_point(self.hero.archer_site[0].pos, self.hero.archer_site[1].pos, free_sites)
                if site:
                    print(f'BUILD {site.id} BARRACKS-ARCHER')
                    return
        print('WAIT')

    def play_phase2(self):
        if len(self.hero.archer_creeps) < 4:
            for archer_site in self.hero.archer_site:
                if gold > cost[ARCHER] and self.in_radius_of_archer(archer_site.pos, 1000):
                    debug(f'TRAIN ARCHER: {self.in_radius_of_archer(archer_site.pos, 400)}')
                    print(f'TRAIN {archer_site.id}')
                    return
        if self.hero.knight_site and len(self.hero.knight_creeps) < 8 and self.hero.knight_site[0].snooze_timer == 0 and gold - 100 > cost[KNIGHT]:
            print(f'TRAIN {self.hero.knight_site[0].id}')
            return
        print('TRAIN')


    def play(self):
        for site in self.sites:
            self.queens[site.owner].archer_site.append(site) if site.type == ARCHER else None
            self.queens[site.owner].knight_site.append(site) if site.type == KNIGHT else None

        for creep in self.creeps:
            self.queens[creep.owner].knight_creeps.append(creep) if creep.type == KNIGHT else None
            self.queens[creep.owner].archer_creeps.append(creep) if creep.type == ARCHER else None

        # Phase 1 wait / build / move
        self.play_phase1()
        # Phase 2 Train commands
        self.play_phase2()
        

num_sites = int(input())
game = Game(num_sites)
for i in range(num_sites):
    site_id, x, y, radius = [int(j) for j in input().split()]
    game.sites[site_id] = Site(site_id, Pos(x,y), radius)
    # debug(f'site_id: {site_id} x: {x} y: {y} radius: {radius}')


# game loop
while True:
    # touched_site: -1 if none
    game.clear()
    gold, touched_site = [int(i) for i in input().split()]
    debug(f'gold: {gold} touched_site: {touched_site}')
    for i in range(num_sites):
        # ignore_1: used in future leagues
        # ignore_2: used in future leagues
        # structure_type: -1 = No structure, 2 = Barracks
        # owner: -1 = No structure, 0 = Friendly, 1 = Enemy
        site_id, ignore_1, ignore_2, structure_type, owner, param_1, param_2 = [int(j) for j in input().split()]
        game.sites[site_id].update(ignore_1, ignore_2, structure_type, owner, param_1, param_2)
        # debug(f'site_id: {site_id} ignore_1:{ignore_1} ignore_2: {ignore_2} structure_type: {owner} param_1: {param_1} param_2: {param_2}')
    num_units = int(input())
    for i in range(num_units):
        # unit_type: -1 = QUEEN, 0 = KNIGHT, 1 = ARCHER
        x, y, owner, unit_type, health = [int(j) for j in input().split()]
        if unit_type == -1:
            game.queens[owner] = Queen(owner, Pos(x,y), health)
            if owner == 0:
                game.hero = game.queens[owner]
        else:
            game.creeps.append(Creep(unit_type, owner, Pos(x,y), health))
        # debug(f'x: {x} y: {y} owner: {owner} unit_type: {unit_type} health: {health}')
        
    # debug(f'Game: {game}', sep='\n')
    # First line: A valid queen action
    # Second line: A set of training instructions
    game.play()

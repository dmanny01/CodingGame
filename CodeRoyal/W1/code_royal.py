import sys
import math

# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.
def debug(*args, **kwargs):
    print(*args, **kwargs, file=sys.stderr)

cost = [80, 100, 140]  # 0 Knight, 1 Archer 2 Giant
KNIGHT = 0
ARCHER = 1
GIANT = 2
FRIENDLY = 0
ENEMY = 1
HOME = None
CODE_RED = 1; CODE_YELLOW = 2; CODE_GREEN = 3

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
        self.towers = list()
        self.archer_site = list()
        self.knight_site = list()
        self.giant_site = list()
        self.knight_creeps = list()
        self.archer_creeps = list()
        self.giant_creeps = list()
        self.mines = list()
        self.total_gold_rate = 0

    def __repr__(self):
        return f'id: {self.id} pos:{self.pos} health: {self.health}'

class Site:
    def __init__(self, id, pos , radius, type=None, owner=None):
        self.id = id
        self.pos = pos
        self.radius = radius
        self.type = None
        self.if_barrack = False
        self.if_tower = False
        self.if_mine = False
        self.owner = None
        self.snooze_timer = 100  # Big Num
        self.health = None
        self.attack_radius = None
        self.remaining_gold = -1
        self.max_mine_rate = None
        self.mine_rate = None

    def update(self, gold, max_mine_rate, structure_type, owner, param_1, param_2):
        self.if_barrack = True if structure_type == 2 else False
        self.if_tower = True if structure_type == 1 else False
        self.if_mine = True if structure_type == 0 else False
        self.owner = owner
        if self.if_barrack:
            self.type = param_2 # -1 -> free 1 -> tower 2 -> barrack
            self.snooze_timer = param_1
        if self.if_tower:
            self.health = param_1
            self.attack_radius = param_2
        if self.if_mine:
            self.mine_rate = param_1
        self.remaining_gold = gold
        self.max_mine_rate = max_mine_rate


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

    def min_distance_site(self, sites,  pos):
        result, min_dist = None, sys.maxsize
        for site in sites:
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
        min_y, max_y = max(pos.x-r, 0), min(pos.x+r, 1920)
        result = list(filter(lambda e: min_x < e.pos.x < max_x and min_y < e.pos.y < max_y, self.queens[ENEMY].knight_creeps))
        return result

    def in_radius_of_tower(self):
        hero = self.hero
        result = list()
        for site in self.hero.towers:
            pos, r = site.pos, site.attack_radius
            min_x, max_x = max(pos.x-r, 0), min(pos.x+r, 1920)
            min_y, max_y = max(pos.x-r, 0), min(pos.x+r, 1920)
            if min_x < hero.pos.x < max_x and min_y < hero.pos.y < max_y:
                result.append(site)
        return result

    @staticmethod
    def in_home_boundary(site):
        d = abs(site.pos.x - HOME.x)
        # debug(f'dist from home: {d} {d < 1920/2}')
        return  d < 1920/2

    def calculate_risk(self):
        result = self.min_distance_site(self.queens[ENEMY].knight_creeps, self.hero.pos)
        debug(f'All enemy creeps: {self.queens[ENEMY].knight_creeps}')
        debug(f'Nearest enemy creep: {result}')
        if not result:
            return CODE_GREEN
        d = self.dist(result.pos, self.hero.pos)
        if d < 200:
            return CODE_RED
        elif 200 < d < 700:
            return CODE_YELLOW
        else:
            return CODE_GREEN

    def play_phase1(self):
        free_sites = sorted([site for site in self.sites if not site.if_barrack and not site.if_tower and not site.if_mine and self.in_home_boundary(site)], key=lambda site:self.dist(self.hero.pos, site.pos))
        # enemy_circle = [(max(site.pos.x-site.attack_radius, 0), min(site.pos.x+site.attack_radius, 1920), max(site.pos.y-site.attack_radius, 0), min(site.pos.y+site.attack_radius, 1000)) for site in self.queens[ENEMY].giant_site]
        code = self.calculate_risk()
        debug(f'Code: {code}')
        if code == CODE_GREEN or code == CODE_YELLOW:
            if free_sites:
                if not self.hero.knight_site:
                    site = free_sites.pop(0)
                    print(f'BUILD {site.id} BARRACKS-KNIGHT')
                    return
                if len(self.hero.mines) < 2:
                    free_sites_around_home = sorted([site for site in self.sites if not site.if_barrack and not site.if_mine and not site.remaining_gold == 0], key=lambda site:self.dist(HOME, site.pos))
                    if free_sites_around_home:
                        site = free_sites_around_home.pop(0)
                    print(f'BUILD {site.id} MINE')
                    return

                if not len(self.hero.towers) < 4:
                    site = free_sites.pop(0)
                    print(f'BUILD {site.id} TOWER')
                    return

                if not self.hero.giant_site and len(self.queens[ENEMY].towers) >= 3:
                    site = free_sites.pop(0)
                    print(f'BUILD {site.id} BARRACKS-GIANT')
                    return

                if self.hero.total_gold_rate < 6:
                    site = None
                    upgradable_mines = [mine for mine in self.hero.mines if mine.mine_rate < mine.max_mine_rate]
                    if upgradable_mines:
                        site = upgradable_mines.pop(0)
                    else:
                        free_sites_around_home = sorted([site for site in self.sites if not site.if_barrack and not site.if_tower and not site.if_mine and not site.remaining_gold == 0], key=lambda site:self.dist(HOME, site.pos))
                        if free_sites_around_home:
                            site = free_sites_around_home.pop(0)
                    print(f'BUILD {site.id} MINE')
                    return
                # free_sites_around_mines = sorted([site for site in self.sites if not site.if_barrack and not site.if_tower and not site.if_mine], key=lambda site:self.dist(self.HOME, site.pos))
                if len(self.hero.towers) < 4:
                        site = free_sites.pop(0)
                        print(f'BUILD {site.id} TOWER')
                        return

            if self.hero.towers: # grow towers
                site = self.min_distance_site(self.hero.towers, self.hero.pos)
                print(f'BUILD {site.id} TOWER')
                return


        if code == CODE_RED:
            # Move away to the safety towards nearest arch/giant site or home
            pos = None
            for site in self.hero.towers:  # grow towers
                all_towers = self.in_radius_of_tower()
                site = self.min_distance_site(all_towers, self.hero.pos)
                if site:
                    print(f'BUILD {site.id} TOWER')
                    return
            if not pos and len(self.hero.towers):
                site = self.min_distance_site(self.hero.towers, self.hero.pos)
                if free_sites and self.dist(free_sites[0].pos, self.hero.pos) < self.dist(site.pos, self.hero.pos):
                    site = free_sites.pop(0)
                    if site and self.dist(site.pos, self.hero.pos) < self.dist(HOME, self.hero.pos):
                        print(f'BUILD {site.id} TOWER')
                        return
                pos = site.pos if site else None
            if not pos and len(self.hero.archer_site):
                site = self.min_distance_site(self.hero.archer_site, self.hero.pos)
                pos = site.pos if site else None
            if not pos and len(self.hero.giant_site):
                site = self.min_distance_site(self.hero.giant_site, self.hero.pos)
                pos = site.pos if site else None
            if not pos:
                if free_sites:
                    site = free_sites.pop(0)
                    if site and self.dist(site.pos, self.hero.pos) < self.dist(HOME, self.hero.pos):
                        print(f'BUILD {site.id} TOWER')
                        return
                    pos = HOME
            debug(f'MOVE {pos.x}, {pos.y}')
            print(f'MOVE {pos.x} {pos.y}')
            return
        print('WAIT')

    def play_phase2(self):
        code = self.calculate_risk()
        if len(self.hero.archer_creeps) < 4:
            for archer_site in self.hero.archer_site:
                if gold > cost[ARCHER] and self.in_radius_of_archer(archer_site.pos, 1000):
                    debug(f'TRAIN ARCHER: {self.in_radius_of_archer(archer_site.pos, 1000)}')
                    print(f'TRAIN {archer_site.id}')
                    return
        if self.hero.knight_site and len(self.hero.knight_creeps) < 6 and self.hero.knight_site[0].snooze_timer == 0 and gold > cost[KNIGHT]:
            print(f'TRAIN {self.hero.knight_site[0].id}')
            return
        if self.hero.giant_site and len(self.hero.giant_creeps) < 1 and len(self.queens[ENEMY].towers) > 4 and self.hero.giant_site[0].snooze_timer == 0 and gold > cost[GIANT]:
            print(f'TRAIN {self.hero.giant_site[0].id}')
            return
        print('TRAIN')

    def play(self):
        for site in self.sites:
            self.queens[site.owner].archer_site.append(site) if site.type == ARCHER else None
            self.queens[site.owner].knight_site.append(site) if site.type == KNIGHT else None
            self.queens[site.owner].giant_site.append(site) if site.type == GIANT else None
            self.queens[site.owner].towers.append(site) if site.if_tower else None
            self.queens[site.owner].mines.append(site) if site.if_mine else None

        for creep in self.creeps:
            self.queens[creep.owner].knight_creeps.append(creep) if creep.type == KNIGHT else None
            self.queens[creep.owner].archer_creeps.append(creep) if creep.type == ARCHER else None
            self.queens[creep.owner].giant_creeps.append(creep) if creep.type == GIANT else None

        self.queens[FRIENDLY].total_gold_rate = sum(mine.mine_rate for mine in self.hero.mines) if self.hero.mines else 0
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
        # debug(f'site_id: {site_id} ignore_1:{ignore_1} ignore_2: {ignore_2} owner: {owner} structure_type:{structure_type} param_1: {param_1} param_2: {param_2}')
    num_units = int(input())
    for i in range(num_units):
        # unit_type: -1 = QUEEN, 0 = KNIGHT, 1 = ARCHER
        x, y, owner, unit_type, health = [int(j) for j in input().split()]
        if unit_type == -1:
            game.queens[owner] = Queen(owner, Pos(x,y), health)
            if owner == 0:
                game.hero = game.queens[owner]
                if not HOME:
                    if game.hero.pos.x < 1920/2:
                        HOME = Pos(0, 0)
                    else:
                        HOME = Pos(1920, 1000)

        else:
            game.creeps.append(Creep(unit_type, owner, Pos(x,y), health))
        # debug(f'x: {x} y: {y} owner: {owner} unit_type: {unit_type} health: {health}')

    # debug(f'Game: {game}', sep='\n')
    # First line: A valid queen action
    # Second line: A set of training instructions
    game.play()

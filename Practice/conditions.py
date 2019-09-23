import sys
import math

# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.
# ---
# Hint: You can use the debug stream to print initialTX and initialTY, if Thor seems not follow your orders.

# light_x: the X position of the light of power
# light_y: the Y position of the light of power
# initial_tx: Thor's starting X position
# initial_ty: Thor's starting Y position
sign = lambda x: x and (1, -1)[x < 0]
start_x, start_y = 0, 0
finish_x, finish_y = 40, 17
light_x, light_y, initial_tx, initial_ty = [int(i) for i in input().split()]
quadrants = {(1, -1): 'NE', (-1, -1): 'NW', (-1, 1): 'SW', (1, 1): 'SE', (1, 0): 'E', (0, -1): 'N', (-1, 0): 'W',
             (0, 1): 'S'}
def timeit(method):
    import time

    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts) * 1000)
        else:
            print('%r  %2.2f ms' %
                  (method.__name__, (te - ts) * 1000))
        return result
    return timed

@timeit
def minsteps(light_x, light_y, initial_tx, initial_ty):
    result = list()
    diff_x = light_x - initial_tx
    diff_y = light_y - initial_ty
    quad_key = sign(diff_x), sign(diff_y)
    quad = quadrants.get(quad_key)
    if not quad:
        return result
    n_quad_steps = min(abs(diff_x), abs(diff_y))
    result += n_quad_steps * [quad]

    # walk across axis
    temp = diff_x - quad_key[0] * n_quad_steps, diff_y - quad_key[1] * n_quad_steps
    n_quad_steps = abs(temp[0]) if abs(temp[0]) > abs(temp[1]) else abs(temp[1])
    quad_key = tuple(map(sign, temp))
    quad = quadrants.get(quad_key)
    if quad:
        result += n_quad_steps * [quad]
    return result

# game loop
while True:
    remaining_turns = int(input())  # The remaining amount of turns Thor can move. Do not remove this line.

    # Write an action using print
    # To debug: print("Debug messages...", file=sys.stderr)

    # A single line providing the move to be made: N NE E SE S SW W or NW
    for i in minsteps(light_x, light_y, initial_tx, initial_ty):
        print(i)

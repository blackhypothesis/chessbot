import chessbot.constants as const
import random

move_nr = 0
step = 0
delta = 0

while True:
    rand = random.uniform(0, 1)
    if rand < const.BEST_MOVE_PROBABILITY:
        move_nr = 0
    else:
        step = (1 - const.BEST_MOVE_PROBABILITY) / const.MULTI_PV
        delta = rand - const.BEST_MOVE_PROBABILITY
        move_nr = int(delta / step)

    print(move_nr, step, delta, rand)
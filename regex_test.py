import re

output = 'info depth 18 seldepth 28 multipv 3 score cp 32 nodes 18100908 nps 12172769 hashfull 1000 tbhits 0 time 1487 pv c2c4 b8c6 g1f3 e7e5 b1c3 d7d6 d2d3 g8f6 f1e2 f8e7 e1g1 e8g8 c3d5 f6d5 c4d5 c6d4 f3d4 c5d4 c1d2 f7f5 f2f4 f5e4 d3e4 c8d7 a2a4 a8c8 f4f5'

result = re.search('^info depth (\d+) seldepth (\d+) multipv (\d+) score ([a-z]+) (\-?\d+) \w* ?nodes (\d+) nps (\d+)(?: hashfull |)(\d+|) tbhits (\d+) time (\d+) pv (.*)', output)
depth = result.group(1)
seldepth = result.group(2)
multipv = result.group(3)
score_type = result.group(4)
score = result.group(5)
nodes = result.group(6)
nps = result.group(7)
move_list = result.group(11)

multipv = int(multipv)
score = int(score)

print(depth, seldepth, multipv, score_type, score, nodes, nps)
print(f'move_list: __{move_list}')


result = re.search('^(\w+) ', move_list)
move = result.group(1)
print(move)
print('----------------')

multi_pv_moves = [{depth: -1, score: 0, move: '-'}] * 3

multi_pv_moves[0] = {"score": -34, "move": 'e3e4'}
multi_pv_moves[1] = {"score": -54, "move": 'g8f6'}

multi_pv_moves[2] = {"score": -54, "move": 'g8f6'}
multi_pv_moves = [{"depth": -1, "score": 0, "move": '-'}] * 3
for m in multi_pv_moves:
    print(m)

i = 2
while True:
    if multi_pv_moves[i]['score'] > 0:
        break

    i = i - 1
    if i == -1:
        break

selected_score = multi_pv_moves[i]['score']
selected_move = multi_pv_moves[i]['move']

print(f'#: {i}, score: {selected_score}, move: {selected_move}')


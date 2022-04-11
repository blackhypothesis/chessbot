# 2540 x 1440
x0 = 750
y0 = 260
# 1920 x 1080
# x0 = 545
# y0 = 205

LICHESS_LOGIN = 'https://lichess.org/login'
BASE_URL = 'https://lichess.org/'
TV_URL = 'https://lichess.org/tv'
# Play anonymous
ANON = True
# lichess tv
TV = False

STOCKFISH = '/home/marcel/bin/stockfish'

# setoption name Threads value
THREADS = 10
# Time Format
TF = 3
# go depth
# 1 + 0 -> 16
MAX_DEPTH = 16
# playing strength
SCORE_LOSS_MIN = 0
SCORE_LOSS_MAX = 450
SCORE_LOSS_INCREASE = 35
BEST_MOVE_PROBABILITY = 0.1
# setoption name MultiPV value
MULTI_PV = 4

LOG_FILE_PATH = '/home/tluluma3/tmp'
DEBUG = True

TIME_FORMAT = ''

if TF == 3:
    TIME_FORMAT = '// * [ @ id = "main-wrap"] / main / div[2] / div[2] / div[3]'
if TF == 2:
    TIME_FORMAT = '//*[@id="main-wrap"]/main/div[2]/div[2]/div[2]'
if TF == 1:
    TIME_FORMAT = '//*[@id="main-wrap"]/main/div[2]/div[2]/div[1]/div[1]'

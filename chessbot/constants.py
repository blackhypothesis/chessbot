x0 = 750
y0 = 260
board_size = 1048

USERNAME = 'albertoslipmouse'
PASSWORD = 'Ishee4bo'

LICHESS_LOGIN = 'https://lichess.org/login'
BASE_URL = 'https://lichess.org/'

# setoption name Threads value
THREADS = 8
# Time Format
TF = 1
# go depth
# 1 + 0 -> 16
MAX_DEPTH = 12
# playing strength
SCORE_LOSS_MIN = 0
SCORE_LOSS_MAX = 450
SCORE_LOSS_INCREASE = 30
BEST_MOVE_PROBABILITY = 0.1
# setoption name MultiPV value
MULTI_PV = 4

LOG_FILE = f'/home/marcel/tmp/{USERNAME}.log'
DEBUG = True

TIME_FORMAT = ''

if TF == 3:
    TIME_FORMAT = '// * [ @ id = "main-wrap"] / main / div[2] / div[2] / div[3]'
if TF == 2:
    TIME_FORMAT = '//*[@id="main-wrap"]/main/div[2]/div[2]/div[2]'
if TF == 1:
    TIME_FORMAT = '//*[@id="main-wrap"]/main/div[2]/div[2]/div[1]/div[1]'

import chessbot.constants as const
from chessbot.lichess import Lichess
import logging
import time
from stockfish import Stockfish

main_logger = logging.getLogger()
main_logger.setLevel(logging.INFO)

logging.basicConfig(
    filename=f'{const.LOG_FILE_PATH}/chessbot.log',
    format="%(asctime)-15s [%(levelname)s] %(funcName)s: %(message)s",
    level=logging.INFO)


# stockfish = Stockfish(path="/home/tluluma3/bin/stockfish", depth=16, parameters={"Threads": 8, "Hash": 4096})
stockfish = Stockfish(path="/home/tluluma3/bin/stockfish", depth=18, parameters={"Threads": 8, "Hash": 4096})

lc = Lichess()
# lc.get_external_ip()
# time.sleep(1)
lc.open_page('https://lichess.org/')
# wait, to load page
time.sleep(3)
if const.ANON == False:
    lc.login('login', 'passwd')
    time.sleep(3)
# lc.select_timeformat('1+0')
lc.select_timeformat('2+1')

# lc.select_play_computer()

while True:
    board_orientation = lc.new_game()

    while True:
        game_state = lc.get_game_state()
        if game_state == 'finished':
            lc.get_player_names()
            lc.get_move_list()
            lc.get_new_opponent()
            break

        if lc.is_new_move():
            half_moves = lc.get_number_of_half_moves()

            if board_orientation == 'white' and half_moves % 2 == 0 or board_orientation == 'black' and half_moves %2 == 1:
                while True:
                    try:
                        fen = lc.get_fen()
                        stockfish.set_fen_position(fen)
                        best_move = stockfish.get_best_move()
                        print(best_move, stockfish.get_evaluation())
                        # time.sleep(2)
                        if half_moves > 16:
                            lc.play_move(best_move)
                        # print(stockfish.get_evaluation() ,stockfish.get_wdl_stats())
                        break
                    except BaseException as e:
                        print(e)
                        continue

            else:
                if half_moves > 2 and half_moves % 30 < 2:
                    pass
                    # lc.give_more_time()

        time.sleep(0.1)

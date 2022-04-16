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


stockfish = Stockfish(path="/home/tluluma3/bin/stockfish", depth=17, parameters={"Threads": 8})

lc = Lichess()
# lc.get_external_ip()
time.sleep(1)
lc.open_page('https://lichess.org/')
# wait, to load page
time.sleep(1)
# lc.login('login', 'pwd')
time.sleep(3)
lc.select_timeformat('1+0')

while True:
    lc.new_game()
    board_orientation = lc.get_board_orientation()

    while True:
        game_state = lc.get_game_state()
        if game_state == 'finished':
            lc.get_player_names()
            move_list = lc.get_move_list()
            main_logger.info(f'Movelist: {move_list}')
            lc.get_new_opponent()
            break

        if lc.is_new_move():
            half_moves = lc.get_number_of_half_moves()

            # if half_moves < 12:
            #     continue

            if board_orientation == 'white' and half_moves % 2 == 0 or board_orientation == 'black' and half_moves %2 == 1:
                while True:
                    try:
                        fen = lc.get_fen()
                        stockfish.set_fen_position(fen)
                        best_move = stockfish.get_best_move()[:4]
                        lc.play_move(best_move)
                        break
                    except BaseException as e:
                        print(e)
                        continue

        time.sleep(0.1)

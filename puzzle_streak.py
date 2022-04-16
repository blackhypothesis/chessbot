import chessbot.constants as const
from chessbot.lichess import Lichess
import logging
import time
from stockfish import Stockfish

main_logger = logging.getLogger()
main_logger.setLevel(logging.DEBUG)

logging.basicConfig(
    filename=f'{const.LOG_FILE_PATH}/chessbot.log',
    format="%(asctime)-15s [%(levelname)s] %(funcName)s: %(message)s",
    level=logging.INFO)


stockfish = Stockfish(path="/home/tluluma3/bin/stockfish", depth=20, parameters={"Threads": 8})

lc = Lichess()
lc.open_page('https://lichess.org/streak')
# wait, to load page
time.sleep(1)
lc.set_modus('puzzle')
lc.toggle_puzzle_autonext()

while True:
    lc.new_game()
    while True:
        time.sleep(0.5)
        puzzle_state = lc.get_puzzle_state()
        if puzzle_state == 'finished':
            main_logger.debug('wait ...')
            time.sleep(0.5)
            lc.puzzle_continue()
            break
        else:
            while True:
                try:
                    fen = lc.get_fen()
                    stockfish.set_fen_position(fen)
                    best_move = stockfish.get_best_move()
                    main_logger.info(f'Best Move: {best_move}')
                    lc.play_move(best_move)
                    time.sleep(0.5)
                    break
                except BaseException as e:
                    print(e)
                    continue



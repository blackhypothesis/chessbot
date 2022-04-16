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
    board_orientation = lc.get_board_orientation()
    depth = int(lc.get_puzzle_elo() / 100) - 2
    stockfish.set_depth(depth)
    main_logger.info(f'set depth: {depth}')

    while True:
        puzzle_state = lc.get_puzzle_state()
        if puzzle_state == 'finished':
            time.sleep(0.3)
            lc.puzzle_continue()
            time.sleep(0.7)
            break

        if lc.is_new_move():
            half_moves = lc.get_number_of_half_moves()

            if board_orientation == 'white' and half_moves % 2 == 0 or board_orientation == 'black' and half_moves % 2 == 1:
                while True:
                    try:
                        fen = lc.get_fen()
                        stockfish.set_fen_position(fen)
                        best_move = stockfish.get_best_move()
                        main_logger.info(f'Best Move: {best_move}')
                        lc.play_move(best_move)
                        break
                    except BaseException as e:
                        print(e)
                        continue



import chessbot.constants as const
import chess
import chess.engine
from chessbot.lichess import Lichess
import logging
import time

main_logger = logging.getLogger()
main_logger.setLevel(logging.INFO)

logging.basicConfig(
    filename=f'{const.LOG_FILE_PATH}/chessbot.log',
    format="%(asctime)-15s [%(levelname)s] %(funcName)s: %(message)s",
    level=logging.INFO)


engine = chess.engine.SimpleEngine.popen_uci("stockfish")
engine.configure({"Threads": 12})

lc = Lichess()
# lc.get_external_ip()
# time.sleep(1)
lc.open_page('https://lichess.org/')
# wait, to load page
time.sleep(3)
if const.ANON == False:
    lc.login('login', 'passwd')
    time.sleep(3)
lc.select_timeformat('1+0')
# lc.select_timeformat('2+1')
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
                        board = chess.Board(fen)
                        # analyse = engine.analyse(board, chess.engine.Limit(depth=17), multipv=1)
                        calc_time = 0.4
                        if half_moves > 60:
                            calc_time = 0.1
                        analyse = engine.analyse(board, chess.engine.Limit(time=calc_time), multipv=1)
                        print(analyse)
                        best_move = analyse[0]["pv"][0].uci()
                        score = analyse[0]["score"].white().score()
                        if half_moves > -1:
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

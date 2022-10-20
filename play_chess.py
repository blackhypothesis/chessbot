import chessbot.constants as const
import chess.engine
from chessbot.lichess import Lichess
import logging
import time

main_logger = logging.getLogger()
main_logger.setLevel(logging.INFO)


def asymp(x, v):
    return 1 - x / (x + v)


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
if not const.ANON:
    lc.login('login', 'passwd')
    time.sleep(3)
lc.select_timeformat('1+0')
# lc.select_timeformat('2+1')
# lc.select_play_computer()

step = 10

while True:
    board_orientation = lc.new_game()
    board = chess.Board()

    while True:
        game_state = lc.get_game_state()
        if game_state == 'finished':
            lc.get_player_names()
            lc.get_move_list()
            lc.get_new_opponent()
            break

        if lc.is_new_move():
            half_moves = lc.get_number_of_half_moves()

            if board_orientation == 'white' and half_moves % 2 == 0 or board_orientation == 'black' and half_moves % 2 == 1:
                while True:
                    try:
                        last_move = lc.get_last_move()
                        if last_move != "":
                            board.push_san(last_move)
                        print("last_move: ", last_move)
                        print(board)

                        multi_pv = 5
                        if half_moves > 30:
                            multi_pv = 1
                        # analyse = engine.analyse(board, chess.engine.Limit(depth=17), multipv=1)
                        calc_time = 0.3
                        analyse = engine.analyse(board, chess.engine.Limit(time=calc_time), multipv=multi_pv)

                        for a in reversed(analyse):
                            print("depth: ", a['depth'], "score: ", a['score'].white().score(), "move: ", a['pv'][0].uci())

                        best_move = analyse[0]["pv"][0].uci()
                        best_score = analyse[0]["score"].white().score()
                        move = best_move
                        score = 0

                        if not analyse[0]["score"].is_mate():
                            max_loss = int(asymp(step, 0.8) * 1000)

                            for a in reversed(analyse):
                                if a['score'].is_mate():
                                    continue
                                score = a['score'].white().score()
                                if abs(best_score - score) < max_loss:
                                    move = a['pv'][0].uci()
                                    break

                        step -= 1
                        if step < 0:
                            step = 10

                        print("score: ", score, "move: ", move, "best_score", best_score, "max loss:", max_loss, "step: ", step)
                        print('\n')

                        if half_moves > -1:
                            lc.play_move(move)
                            board.push_uci(move)
                        break
                    except BaseException as e:
                        print(e)
                        continue

            else:
                if half_moves > 2 and half_moves % 30 < 2:
                    pass
                    # lc.give_more_time()

        time.sleep(0.1)

import chessbot.constants as const
import logging
import random
import time
import re
from chessbot.chessbot import Chessbot
from subprocess import Popen, PIPE
from chessbot.nbstreamreader import NonBlockingStreamReader as NBSR


mainlogger = logging.getLogger(__name__)
mainlogger.setLevel(logging.DEBUG)

logging.basicConfig(
    filename=f'{const.LOG_FILE_PATH}/chessbot.log',
    format="%(asctime)-15s [%(levelname)s] %(funcName)s: %(message)s",
    level=logging.INFO)

# run stockfish as a subprocess:
p = Popen([const.STOCKFISH],
          stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=False, universal_newlines=True)
# wrap p.stdout with a NonBlockingStreamReader object:
nbsr = NBSR(p.stdout)

mainlogger.info('Initialize Stockfish')

for cmd in 'stop', \
           f'setoption name Threads value {const.THREADS}', \
           f'setoption name MultiPV value {const.MULTI_PV}', \
           'd', \
        :
    p.stdin.write(f'{cmd}\n')
    p.stdin.flush()
    mainlogger.info(f'CMD: {cmd}')

    while True:
        output = nbsr.readline(0.5)
        # 0.5 secs to let the shell output the result
        if not output:
            print('### END of data ###')
            break
        output = output[:-1]
        mainlogger.info(f'SF: {output}')

mainlogger.info('############################## start ##############################')
mainlogger.info('###################################################################')
mainlogger.info('###################################################################')

with Chessbot(teardown=False) as bot:
    ext_ip = bot.get_external_ip()
    mainlogger.info(f'External IP: {ext_ip}')

    if not const.ANON:
        bot.chess_login()
    elif not const.TV:
        bot.land_first_page(const.BASE_URL)
    else:
        bot.land_first_page(const.TV_URL)

    # wait a second, till the page is loaded
    time.sleep(2)

    if not const.TV:
        bot.select_game()

    while True:
        orientation = bot.get_board_orientation()
        while orientation is None:
            orientation = bot.get_board_orientation()

        bot.get_board_size()
        bot.get_board_location()
        print(f'orientation = {orientation}')
        bot.get_cg_board_element()

        fen_old = ''
        score_loss_current = const.SCORE_LOSS_MIN

        # old number of half moves
        old_number_half_moves = bot.get_number_of_half_moves()
        if old_number_half_moves == 0:
            old_number_half_moves = -2
        mainlogger.info(f'old_number_half_moves: {old_number_half_moves}')

        while True:
            best_move = ''
            fen = ''

            ricons = bot.get_ricons()
            if ricons is None:
                bot.get_player_names()
                move_list = bot.get_move_list()
                mainlogger.info(f'Movelist: {move_list}')
                mainlogger.info('### --- GAME FINISHED --- ###')
                bot.reset()

                if not const.TV:
                    time.sleep(5)
                    bot.get_new_opponent()

                break

            number_half_moves = bot.get_number_of_half_moves()
            while number_half_moves <= old_number_half_moves and number_half_moves != 1\
                    :
                if orientation == 'white' and number_half_moves % 2 == 1:
                    break
                if orientation == 'black' and number_half_moves % 2 == 0:
                    break
                mainlogger.warning(f'number_half_moves: {number_half_moves} not greater than old_number_half_moves: {old_number_half_moves}')
                number_half_moves = bot.get_number_of_half_moves()
            old_number_half_moves = number_half_moves

            if orientation == 'white' and number_half_moves % 2 == 0:
                fen = bot.go_play()

            if orientation == 'black' and number_half_moves % 2 == 1:
                fen = bot.go_play()

            if 'NO_FEN' in fen:
                mainlogger.warning('### NO_FEN')
                continue

            if fen != fen_old and fen != '':
                mainlogger.info('############################## move ###############################')
                mainlogger.info('###################################################################')
                mainlogger.info(f'number_half_moves = {number_half_moves}')

                fen_old = fen

                fen_cmd = f'position fen {fen}'

                for cmd in 'stop', fen_cmd, \
                           'd', \
                           f'go depth {const.MAX_DEPTH}', \
                        :
                    p.stdin.write(f'{cmd}\n')
                    p.stdin.flush()
                    mainlogger.info(f'CMD: {cmd}')
                    p.stdin.write('isready\n')
                    p.stdin.flush()

                multi_pv_moves = [{"depth": -1, "score": 0, "move": '-'}] * const.MULTI_PV

                while True:
                    depth = 0
                    output = nbsr.readline(0.1)
                    # 0.1 secs to let the stockfish output the result

                    if not output:
                        mainlogger.info('SF: ### END of data ###')
                    else:
                        output = output[:-1]
                        if 'info depth' not in output:
                            mainlogger.info(f'SF: {output}')

                        if 'bestmove' in output:
                            best_move = output
                            break

                        try:
                            result = re.search(r'^info depth (\d+) seldepth (\d+) multipv (\d+) score ([a-z]+) (\-?\d+) \w* ?nodes (\d+) nps (\d+)(?: hashfull |)(\d+|) tbhits (\d+) time (\d+) pv (.*)', output)
                            depth = result.group(1)
                            seldepth = result.group(2)
                            multipv = result.group(3)
                            score_type = result.group(4)
                            score = result.group(5)
                            nodes = result.group(6)
                            nps = result.group(7)
                            move_list = result.group(11)

                            depth = int(depth)
                            multipv = int(multipv)
                            score = int(score)

                            if depth > const.MAX_DEPTH - 2:
                                mainlogger.info(f'SF> {output}')

                            if score_type == 'mate':
                                if score < 0:
                                    score = -15000 - score - 1
                                else:
                                    score = 15000 - score + 1

                            result = re.search(r'^(\w+)( |$)', move_list)
                            move = result.group(1)
                            # print(f'multipv: {multipv}, move: {move}')

                            multi_pv_moves[multipv - 1] = {"depth": depth, "score": score, "move": move}
                        except:
                            continue

                print('multi_pv_moves')
                for m in multi_pv_moves:
                    print(m)

                rand = random.uniform(0, 1)
                if rand < const.BEST_MOVE_PROBABILITY:
                    move_nr = 0
                else:
                    step = (1 - const.BEST_MOVE_PROBABILITY) / const.MULTI_PV
                    delta = rand - const.BEST_MOVE_PROBABILITY
                    move_nr = int(delta / step)

                move_nr = move_nr + 1
                while True:
                    move_nr = move_nr - 1
                    if move_nr == -1:
                        move_nr = 0
                        break

                    # no move
                    if multi_pv_moves[move_nr]['depth'] == -1:
                        continue
                    # if the move loses less then score_loss_current, choose this move
                    elif multi_pv_moves[move_nr]['score'] > multi_pv_moves[0]['score'] - score_loss_current:
                        break

                    if move_nr == 0:
                        break

                # increase the current score loss every time.
                # this will increase the probability to make a bigger blunder
                score_loss_current = score_loss_current + const.SCORE_LOSS_INCREASE

                if score_loss_current > const.SCORE_LOSS_MAX:
                    score_loss_current = const.SCORE_LOSS_MAX

                # calculate score_loss
                # the score from the best move compaired to the score to the selected move
                score_loss = multi_pv_moves[0]['score'] - multi_pv_moves[move_nr]['score']

                # if not the best move was choosen, the score loss is greater than 0.
                # substract the score loss from the current score loss
                # this prevents to make several big blunders in a row
                score_loss_current = score_loss_current - score_loss

                selected_score = multi_pv_moves[move_nr]['score']
                selected_move = multi_pv_moves[move_nr]['move']

                print(f'Selected move: #: {move_nr + 1}, move: {selected_move}, score: {selected_score}, score_loss: {score_loss} [{score_loss_current}], rand: {rand}')

                # wait some time to make the reaction time arbitrary
                # only if timeformat is not bullet
                if const.TF != 1:
                    if number_half_moves > 12:
                        seconds = bot.get_time_left_seconds()
                        if seconds is None:
                            mainlogger.warning('cannot get time left in seconds')
                        else:
                            mainlogger.info(f'{seconds} seconds left')
                            if seconds > 30:
                                wait_seconds = random.uniform(0.3, 7.0)
                                if seconds < 60:
                                    wait_seconds = wait_seconds / 2
                                mainlogger.info('wait ' + '{0:.2f}'.format(wait_seconds) + ' seconds' )
                                time.sleep(wait_seconds)

                mainlogger.info(f'###--- PLAY SELECTED MOVE: #: {move_nr+1}, score: {selected_score}, move: {selected_move} score_loss: {score_loss} [{score_loss_current}]---###')

                if not const.TV:
                    bot.play_move(selected_move)

            time.sleep(0.2)

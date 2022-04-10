import chessbot.constants as const
from chessbot.lichess import Lichess
import logging

main_logger = logging.getLogger()
main_logger.setLevel(logging.DEBUG)

logging.basicConfig(
    filename=f'{const.LOG_FILE_PATH}/chessbot.log',
    format="%(asctime)-15s [%(levelname)s] %(funcName)s: %(message)s",
    level=logging.INFO)


lc = Lichess()
lc.open_page('https://lichess.org/tv')

lc.new_game()
fen = lc.get_fen()

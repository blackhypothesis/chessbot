from chessbot.chessbot import Chessbot
import time

with Chessbot(teardown=False) as bot:
    bot.land_first_page()

    bot.mouse_move("e", "2")
    time.sleep(1)
    bot.mouse_move("e", "4")
    time.sleep(1)
    bot.mouse_move("b", "8")
    time.sleep(1)
    bot.mouse_move("c", "6")
    time.sleep(1)

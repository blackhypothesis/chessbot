from chessbot.lichess import Lichess

lc = Lichess()
lc.open_page('https://lichess.org/tv')

while True:
    lc.new_game()
    lc.get_position_of_pieces()
    fen = lc.get_fen()
    print(fen)

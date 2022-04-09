import chessbot.constants as const
import chessbot.credentials as cred
import time
import logging
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
import pyautogui
import re

botlogger = logging.getLogger(__name__)
botlogger.setLevel(logging.INFO)
logging.getLogger('selenium').setLevel(logging.ERROR)
logging.getLogger('pyautogui').setLevel(logging.ERROR)

logging.basicConfig(
    filename=f'{const.LOG_FILE_PATH}/chessbot.log',
    format="%(asctime)-15s [%(levelname)s] %(funcName)s: %(message)s",
    level=logging.INFO)


class Chessbot(webdriver.Chrome):
    # orientation: white -> white is on bottom
    #              black -> black is on bottom
    orientation = 'white'
    # color, which has to make the next move
    active_color = 'w'
    # chess board
    board = [['empty field'] * 8 for _ in range(8)]
    # board size
    board_x_size = 0
    board_y_size = 0
    # board_location
    board_x_location = 0
    board_y_location = 0
    # last move piece
    last_move_piece = ''
    # cg_board contains all pieces on the board and the last move
    cg_board = None
    # count half moves
    half_moves = 0
    # status castling right
    # if a pieces has already moved and the moved back to the origin square, the castling right
    # will not get back
    status_castling_right = 'KQkq'

    def __init__(self, driver_path=r"~/bin", teardown=False):
        self.driver_path = driver_path
        self.teardown = teardown
        os.environ['PATH'] += self.driver_path
        super(Chessbot, self).__init__()
        self.implicitly_wait(1)
        self.maximize_window()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.teardown:
            self.quit()

    def reset(self):
        self.status_castling_right = 'KQkq'

    def chess_login(self):
        self.get(const.LICHESS_LOGIN)
        botlogger.info(f'Login Page: {const.LICHESS_LOGIN}')
        username = self.find_element(
            By.ID,
            'form3-username'
        )
        username.clear()
        username.send_keys(cred.USERNAME)

        password = self.find_element(
            By.ID,
            'form3-password'
        )
        password.clear()
        password.send_keys(cred.PASSWORD)

        time.sleep(1)

        submit = self.find_element(
            By.XPATH,
            '//*[@id="main-wrap"]/main/form/div[1]/button'
        )
        submit.click()

    def land_first_page(self, url):
        self.get(url)
        botlogger.debug(f'landing on page: {url}')

    def select_game(self):
        self.find_element(
            By.XPATH,
            const.TIME_FORMAT

        ).click()

    #############################################################################################################

    def go_play(self):
        # FEN string
        fen = ''

        # DEBUG: all child elements
        # self.log_cg_board_elements(self.cg_board)

        status = self.get_position_of_pieces()
        while status == False:
            botlogger.warning('get_position_of_pieces: not able to get all pieces, will try again')
            status = self.get_position_of_pieces()

        # status = self.get_last_move()
        # while status == False:
        #    botlogger.warning('get_last_move: cannot get last move piece, will try again')
        #    status = self.get_last_move()

        # self.get_active_color()
        if self.half_moves % 2 == 0:
            self.active_color = 'w'
        else:
            self.active_color = 'b'

        ######################################################################################################
        # calculate FEN string
        space = 0

        for y in reversed(range(8)):
            for x in range(8):
                result = re.search(r'(\w+) (\w+)', self.board[x][y])
                color = result.group(1)
                piece = result.group(2)

                if piece != 'knight':
                    piece_letter = piece[:1]
                else:
                    piece_letter = piece[1:2]

                if color == 'white':
                    piece_letter = piece_letter.upper()

                if color == 'empty':
                    space += 1
                else:
                    if space > 0:
                        fen += chr(space + 48)
                        space = 0
                    fen += piece_letter

            if space > 0:
                fen += chr(space + 48)
                space = 0
            fen += '/'

        # remove last slash
        fen = fen[:-1]

        # calculate castling right
        # check king position and if rooks are in the corners
        castling_right = ''
        if self.board[4][0] == 'white king':
            if 'K' in self.status_castling_right:
                if self.board[7][0] == 'white rook':
                    castling_right += 'K'
            if 'Q' in self.status_castling_right:
                if self.board[0][0] == 'white rook':
                    castling_right += 'Q'
        if self.board[4][7] == 'black king':
            if 'k' in self.status_castling_right:
                if self.board[7][7] == 'black rook':
                    castling_right += 'k'
            if 'q' in self.status_castling_right:
                if self.board[0][7] == 'black rook':
                    castling_right += 'q'

        if len(castling_right) == 0:
            castling_right = '-'
        self.status_castling_right = castling_right

        fen += f' {self.active_color} {castling_right} - 0 1'
        botlogger.info(f'FEN: {fen}')

        return fen

    ###############################################################################################################
    # play move
    def play_move(self, bm):
        x1 = ord(bm[:1]) - 96 - 1
        y1 = int(bm[1:2]) - 1
        x2 = ord(bm[2:3]) - 96 - 1
        y2 = int(bm[3:4]) - 1

        if self.orientation == 'black':
            x1 = 7 - x1
            y1 = 7 - y1
            x2 = 7 - x2
            y2 = 7 - y2

        botlogger.debug(f'orientation: {self.orientation} active_color: {self.active_color}')
        if self.orientation[:1] == self.active_color:
            self.mouse_move(x1, y1)
            pyautogui.click()
            self.mouse_move(x2, y2)
            pyautogui.click()
            botlogger.debug(f'move: [{x1} {y1}], [{x2} {y2}]')

    def mouse_move(self, cx, cy):
        x_pos = cx * (self.board_x_size / 8) + self.board_x_size / 24 + self.board_x_location
        y_pos = (7 - cy) * (self.board_y_size / 8) + self.board_y_size / 24 + self.board_y_location

        botlogger.debug(f'board_x_location: {self.board_x_location}, board_y_location: {self.board_y_location}, x_pos: {x_pos}, y_pos: {y_pos}')
        pyautogui.moveTo(x_pos, y_pos)

    ###############################################################################################################
    # helper functions
    ###############################################################################################################

    ###############################################################################################################
    # calculate the coorindates of a piece according of the size and orientation of the board
    def get_piece_coordinates(self, piece_coordinates_string, board_x_size, board_y_size):
        result = re.search(r'translate\(([\d\.]+)px, ([\d\.]+)px\)', piece_coordinates_string)

        try:
            x = int(round(float(result.group(1))))
            y = int(round(float(result.group(2))))
        except:
            print(f'ERROR: Regex does not get group from string: {piece_coordinates_string}')
            return -1, -1

        square_x = int(x / (board_x_size / 8) + 0.5) + 1
        square_y = 8 - int(y / (board_y_size / 8) + 0.5)

        if self.orientation == 'black':
            square_x = 9 - square_x
            square_y = 9 - square_y

        return square_x, square_y

    ###############################################################################################################
    # board orientation
    #   white: white is on bottom, bot plays white
    #   black: black is on bottom, bot plays black
    def get_board_orientation(self):
        self.orientation = 'white'
        try:
            coords = self.find_element(
                By.TAG_NAME,
                'coords'
            ).get_attribute('class')
            if coords == 'ranks black':
                self.orientation = 'black'
            botlogger.info(f'orientation: {self.orientation}')
        except:
            self.orientation = None
            if const.DEBUG:
                botlogger.warning('orientation cannot be determined')
        return self.orientation

    ###############################################################################################################
    # board size
    # the board size is needed to calculate where the pieces are located on the board
    def get_board_size(self):
        try:
            cg_container = self.find_element(
                By.TAG_NAME,
                'cg-container'
            )
            size = cg_container.size
            self.board_x_size = size['width']
            self.board_y_size = size['height']

            if const.DEBUG:
                botlogger.info(f'boardsize: {self.board_x_size}, {self.board_y_size}')
        except:
            self.board_x_size = 0
            self.board_y_size = 0

            botlogger.warning('board_size cannot be determined')
        return self.board_x_size, self.board_y_size

    ###############################################################################################################
    # board location
    # the board location cannot be determined absolutely exactly
    def get_board_location(self):
        try:
            board = self.find_element(
                By.TAG_NAME,
                'cg-container'
            )
            location = board.location
            location_x = location['x']
            location_y = location['y']
            # win_location = board.get_window_position('current')
            canvas_x_offset = self.execute_script(
                "return window.screenX + (window.outerWidth - window.innerWidth) / 2 - window.scrollX;")
            canvas_y_offset = self.execute_script(
                "return window.screenY + (window.outerHeight - window.innerHeight) - window.scrollY;")
            self.board_x_location = canvas_x_offset + location_x
            self.board_y_location = canvas_y_offset + location_y
            botlogger.info(f'board_location: board_x_location: {self.board_x_location}, board_y_location: {self.board_y_location}')
        except:
            self.board_x_location = 0
            self.board_y_location = 0
            botlogger.warning('board_location: cannot be determined')

        return self.board_x_location, self.board_y_location

    ###############################################################################################################
    # cg_board
    # this element contains information about the last move and all pieces on the board
    def get_cg_board_element(self):
        try:
            self.cg_board = self.find_element(
                By.TAG_NAME,
                'cg-board'
            )
            botlogger.info('cg_board element found')
        except:
            if const.DEBUG:
                botlogger.warning('cg_board element not available')
            self.cg_board = None

    ######################################################################################################
    # get the position of each piece and populate the squares of the board
    # get list of all pieces on the board
    def get_position_of_pieces(self):
        self.clear_board()
        squares = self.cg_board.find_elements(
            By.TAG_NAME,
            'piece'
        )
        for square in squares:
            try:
                piece = square.get_attribute('class')
                piece_coordinates = square.get_attribute('style')
            except:
                botlogger.warning('cannot get attributes')
                return False

            # if a piece is actually dragged, the current position cannot get properly.
            if 'dragging' in piece:
                botlogger.warning(f'piece dragged: {piece}')
                return False

            square_x, square_y = self.get_piece_coordinates(piece_coordinates, self.board_x_size, self.board_y_size)

            if square_x == -1 or square_x > 8:
                botlogger.warning(f'square_x = {square_x} out of range')
                return False
            if square_y == -1 or square_y > 8:
                botlogger.warning(f'square_y = {square_y} out of range')
                return False

            self.board[square_x - 1][square_y - 1] = piece
            botlogger.debug(f'piece: "{piece}", x: {square_x}, y: {square_y}')

        return True

    ######################################################################################################
    # get the last move
    # get the last move to determine which color has to move
    # last move piece
    def get_last_move(self):
        self.last_move_piece = ''

        try:
            last_move_squares = self.cg_board.find_elements(
                By.TAG_NAME,
                'square'
            )
        except:
            botlogger.warning('No last move')
            return False

        i = 0
        for last_move_square in last_move_squares:
            try:
                last_move_class = last_move_square.get_attribute('class')
                last_move_coordinates = last_move_square.get_attribute('style')
            except:
                botlogger.warning('Last Move: cannot get attribute from last_move_square')
                return False

            botlogger.debug(f'last_move_square: i={i}, class={last_move_class}, coorinates={last_move_coordinates}')
            # if the king is in check, the first element has the class name 'check'
            # this element does point to the king which is in check, but we need the last piece which moved
            # only process class == 'last-move'
            if last_move_class == 'last-move':
                square_x, square_y = self.get_piece_coordinates(last_move_coordinates, self.board_x_size,
                                                                self.board_y_size)
                botlogger.debug(
                    f'last_move_class == last-move last move piece: i={i}, x={square_x}, y={square_y}, last_move_coordinate={last_move_coordinates}')
                if square_x == -1:
                    botlogger.warning(f'square_x = {square_x} out of range')
                    return False

                if i == 0:
                    self.last_move_piece = self.board[square_x - 1][square_y - 1]
                    botlogger.debug(
                        f'i == 0 last move piece: i={i}, x={square_x}, y={square_y}, piece={self.last_move_piece}')

                    if (square_x == 1 or square_x == 8) and (square_y == 1 or square_y == 8):
                        # rochade is from king to corner square, therefore last_move_piece == 'empty field'
                        # if last move was rochade
                        if self.last_move_piece == 'empty field':
                            if square_x == 1 or square_x == 8:
                                if square_y == 1:
                                    self.last_move_piece = 'white king'
                                if square_y == 8:
                                    self.last_move_piece = 'black king'
                            botlogger.debug(
                                f'Rochade: last move piece: i={i}, x={square_x}, y={square_y}, piece={self.last_move_piece}')
                            return True

                    # no rochade and empty -> piece cannot be determined
                    if self.last_move_piece == 'empty field':
                        return False
                    else:
                        return True
                i += 1

    ######################################################################################################
    # calculate active color - which color has to move
    def get_active_color(self):
        try:
            result = re.search(r'(\w+) (\w+)', self.last_move_piece)
            color = result.group(1)
            piece = result.group(2)
        except:
            botlogger.debug(f'last move, cannot get color, piece="{self.last_move_piece}"')
            return 'NO_FEN'

        botlogger.debug(f'active_color: last_move_piece="{self.last_move_piece}", color="{color}"')

        if color == 'white':
            self.active_color = 'b'
        else:
            self.active_color = 'w'

        botlogger.debug(f'active_color = {self.active_color}')

    ###############################################################################################################
    # count half moves
    def get_number_of_half_moves(self):
        try:
            move_list = self.find_element(
                By.TAG_NAME,
                'l4x'
            ).find_elements(
                By.TAG_NAME,
                'u8t'
            )
        except:
            self.half_moves = 0
            return 0

        self.half_moves = len(move_list)
        return self.half_moves

    ###############################################################################################################
    # count half moves
    def get_move_list(self):
        move_list_string = 'N/A'
        try:
            move_list = self.find_element(
                By.TAG_NAME,
                'l4x'
            ).find_elements(
                By.TAG_NAME,
                'u8t'
            )
            move_list_string = ''
            for move in move_list:
                move_list_string = move_list_string + move.text + ' '
        except:
            return ''

        return move_list_string

    ###############################################################################################################
    # get result of game -> then the game is finished
    def get_result(self):
        try:
            botlogger.debug('try to get result, ...')
            result = self.find_element(
                # By.CLASS_NAME,
                # 'result'
                By.XPATH,
                '//*[@id="main-wrap"]/main/div[1]/rm6/l4x/div/p[1]'
            )
            text = result.text
            botlogger.debug(f'after try to get result, result ="{text}"')
        except:
            botlogger.debug('no result')
            return None
        return result.text

    ###############################################################################################################
    # get new opponent
    def get_new_opponent(self):
        new_opponent = self.find_element(
            By.XPATH,
            '//*[@id="main-wrap"]/main/div[1]/div[5]/div/a[1]'
        )
        botlogger.info('clicking on NEW OPPONENT')
        new_opponent.click()

    ###############################################################################################################
    # rematch
    def rematch(self):
        rematch = self.find_element(
            By.XPATH,
            '//*[@id="main-wrap"]/main/div[1]/div[5]/div/button'
        )
        botlogger.info('clicking on REMATCH')
        rematch.click()

    ###############################################################################################################
    # ricons class: is only available if game is running
    def get_ricons(self):
        try:
            ricons = self.find_element(
                By.CLASS_NAME,
                'ricons'
            )
            return ricons.text
        except:
            return None

    ###############################################################################################################
    # debug cg_board child elements
    def log_cg_board_elements(self, cg_board):
        # DEBUG, get all elements
        all_cg_board_elements = cg_board.find_elements(
            # By.CSS_SELECTOR,
            # '*'
            By.CLASS_NAME,
            'last-move'
        )

        for element in all_cg_board_elements:
            try:
                s = 'TAG: ' + element.tag_name + ' CLASS: ' + element.get_attribute(
                    'class') + ' STYLE: ' + element.get_attribute('style')

                if element.tag_name == 'piece':
                    piece_coordinates = element.get_attribute('style')
                    # square_x, square_y = self.get_piece_coordinates(piece_coordinates, board_x_size, board_y_size)
                botlogger.debug(s)
            except:
                botlogger.warning(f'cannot get attributes from element {element}')

    ###############################################################################################################
    # clear board, make it empty
    def clear_board(self):
        for x in range(8):
            for y in range(8):
                self.board[x][y] = 'empty field'

    ###############################################################################################################
    # get elapsed time in seconds from the chess clock
    def get_time_left_seconds(self):
        try:
            # we need only the time of the clock on the bottom.
            clock_bottom = self.find_element(
                By.XPATH,
                '//*[@id="main-wrap"]/main/div[1]/div[8]/div[2]'
            )
        except:
            return None

        min_sec = clock_bottom.get_attribute("textContent")
        minutes = int(min_sec[:2])
        seconds = int(min_sec[3:5])
        return minutes * 60 + seconds

    ###############################################################################################################
    # get user names and rating
    def get_player_names(self):
        bottom_user_name = 'N/A'
        bottom_user_rating = 'N/A'
        upper_user_name = 'N/A'
        upper_user_rating = 'N/A'
        try:
            bottom_user_name = self.find_element(
                By.XPATH,
                '//*[@id="main-wrap"]/main/div[1]/div[5]/a'
            ).text
        except:
            pass

        try:
            bottom_user_rating = self.find_element(
                By.XPATH,
                '//*[@id="main-wrap"]/main/div[1]/div[5]/rating'
            ).text
        except:
            pass

        try:
            upper_user_name = self.find_element(
                By.XPATH,
                '//*[@id="main-wrap"]/main/div[1]/div[4]/a'
            ).text
        except:
            pass

        try:
            upper_user_rating = self.find_element(
                By.XPATH,
                '//*[@id="main-wrap"]/main/div[1]/div[4]/rating'
            ).text
        except:
            pass

        if self.orientation == 'white':
            botlogger.info(
                f'White: {bottom_user_name} [{bottom_user_rating}], Black: {upper_user_name} [{upper_user_rating}]')
        else:
            botlogger.info(
                f'White: {upper_user_name} [{upper_user_rating}], Black: {bottom_user_name} [{bottom_user_rating}]')

    ###############################################################################################################
    # get external IP
    def get_external_ip(self):
        self.get("https://myexternalip.com/")
        ext_ip = self.find_element(By.ID, 'ip').text
        return ext_ip

###############################################################################################################

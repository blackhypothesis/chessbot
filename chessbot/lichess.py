from selenium import webdriver
from selenium.webdriver.common.by import By
import os
import time
import re


class Lichess(webdriver.Chrome):
    def __init__(self, driver_path=r"~/bin", teardown=False):
        self.driver_path = driver_path
        self.teardown = teardown
        os.environ['PATH'] += self.driver_path
        super(Lichess, self).__init__()
        self.implicitly_wait(3)

        self.state = {
            # board_orientation: white -> white is on bottom
            #              black -> black is on bottom
            "board_orientation": "white",
            # color, which has to make the next move
            "active_color": "white",
            # chess board absolute location
            "board_position": {"x": 0, "y": 0},
            # board size
            "board_size": {"x": 0, "y": 0},
            # last move piece
            "last_move_piece": "",
            # count half moves
            "half_moves": 0,
            # status castling right
            # if a pieces has already moved and the moved back to the origin square, the castling right
            # fen string
            "fen": "",
            # castling rights
            "status_castling_right":"KQkq",
            # game state
            "game_state": "finished"
        }
        # cg_board, this is the element, containing the pieces and last move information
        self.cg_board = None
        # board representation
        self.board = [['empty field'] * 8 for _ in range(8)]

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.teardown:
            self.quit()

    ###############################################################################################################
    # new game
    # get information about the board board_orientation, position, size
    # get also the web element cg_board
    def new_game(self):
        self.get_board_board_orientation()
        self.get_board_position()
        self.get_board_size()
        self.get_game_state()

    ###############################################################################################################
    # open web page
    def open_page(self, url: str):
        self.get(url)

    ###############################################################################################################
    # login with username and password
    def login(self, login: str, password: str):
        try:
            username = self.find_element(
                By.ID,
                'form3-username'
            )
            username.clear()
            username.send_keys(login)

            password = self.find_element(
                By.ID,
                'form3-password'
            )
            password.clear()
            password.send_keys(password)

            time.sleep(1)

            submit = self.find_element(
                By.XPATH,
                '//*[@id="main-wrap"]/main/form/div[1]/button'
            )
            submit.click()
        except:
            print('ERROR: cannot login')

    ###############################################################################################################
    # select timeformat
    def select_timeformat(self, timeformat: str):
        if timeformat == '3+0':
            tf_xpath = '//*[@id="main-wrap"]/main/div[2]/div[2]/div[3]'
        elif timeformat == '2+1':
            tf_xpath = '//*[@id="main-wrap"]/main/div[2]/div[2]/div[2]'
        elif timeformat == '1+0':
            tf_xpath = '//*[@id="main-wrap"]/main/div[2]/div[2]/div[1]/div[1]'
        else:
            raise

        try:
            self.find_element(
                By.XPATH,
                tf_xpath

            ).click()
        except:
            print(f'ERROR: cannot choose timeformat: {timeformat}')

    ###############################################################################################################
    # board board_orientation
    #   white: white is on bottom, bot plays white
    #   black: black is on bottom, bot plays black
    def get_board_board_orientation(self):
        try:
            coords = self.find_element(
                By.TAG_NAME,
                'coords'
            ).get_attribute('class')

            if coords == 'ranks black':
                self.state['board_orientation'] = 'black'
            else:
                self.state['board_orientation'] = 'white'
        except:
            print('ERROR: cannot get board board_orientation')

    ###############################################################################################################
    # board absolute position on screen. this cannot be determined precisely, but enough
    # accurate to position the mouse cursor over the board fields to move pieces.
    def get_board_position(self):
        # get the position of the browser window
        # windows_location = self.get_window_position('current')
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
            self.state['board_position']['x'] = canvas_x_offset + location_x
            self.state['board_position']['y'] = canvas_y_offset + location_y
        except:
            print('ERROR: cannot get board position')
        return self.state['board_position']['x'], self.state['board_position']['y']

    ###############################################################################################################
    # get board size
    def get_board_size(self):
        try:
            board = self.find_element(
                By.XPATH,
                '//*[@id="main-wrap"]/main/div[1]/div[1]/div/cg-container'
            )

            self.state['board_size']['x'] = board.size['width']
            self.state['board_size']['y'] = board.size['height']
        except:
            print('Board not available.')
        return self.state['board_size']['x'], self.state['board_size']['y']

    ###############################################################################################################
    # cg_board
    # this element contains information about the last move and all pieces on the board
    def cg_board_element(self):
        try:
            self.cg_board = self.find_element(
                By.TAG_NAME,
                'cg-board'
            )
        except:
            self.cg_board = None
            print('ERROR: cannot get web element cg_board')

    ######################################################################################################
    # get the position of each piece and populate the squares of the board
    # get list of all pieces on the board
    def get_position_of_pieces(self):
        self.cg_board_element()
        # first, clear board
        for x in range(8):
            for y in range(8):
                self.board[x][y] = 'empty field'

        squares = self.cg_board.find_elements(
            By.TAG_NAME,
            'piece'
        )
        piece = None

        piece_coordinates = ''
        for square in squares:
            try:
                piece = square.get_attribute('class')
                piece_coordinates = square.get_attribute('style')
            except:
                print('ERROR: cannot get web element for piece')

            # if a piece is actually dragged, the current position cannot get properly.
            if 'dragging' in piece:
                raise 'piece dragged'

            square_x, square_y = self.get_piece_coordinates(piece_coordinates, self.state['board_size'])
            self.board[square_x - 1][square_y - 1] = piece

    ###############################################################################################################
    # calculate the coorindates of a piece according to the size and board_orientation of the board
    def get_piece_coordinates(self, piece_coordinates_string, board_size):
        result = re.search(r'translate\(([\d\.]+)px, ([\d\.]+)px\)', piece_coordinates_string)

        try:
            x = int(round(float(result.group(1))))
            y = int(round(float(result.group(2))))
        except:
            print(f'ERROR: Regex does not get group from string: {piece_coordinates_string}')
            return -1, -1

        square_x = int(x / (board_size['x'] / 8) + 0.5) + 1
        square_y = 8 - int(y / (board_size['y'] / 8) + 0.5)

        if self.state['board_orientation'] == 'black':
            square_x = 9 - square_x
            square_y = 9 - square_y

        return square_x, square_y

    ######################################################################################################
    # calculate FEN string
    def get_fen(self):
        self.get_position_of_pieces()
        active_color = self.get_active_color()[:1]
        space = 0
        self.state['fen'] = ''

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
                        self.state['fen'] += chr(space + 48)
                        space = 0
                    self.state['fen'] += piece_letter

            if space > 0:
                self.state['fen'] += chr(space + 48)
                space = 0
            self.state['fen'] += '/'

        # remove last slash
        self.state['fen'] = self.state['fen'][:-1]

        # calculate castling right
        # check king position and if rooks are in the corners
        castling_right = ''
        if self.board[4][0] == 'white king':
            if 'K' in self.state['status_castling_right']:
                if self.board[7][0] == 'white rook':
                    castling_right += 'K'
            if 'Q' in self.state['status_castling_right']:
                if self.board[0][0] == 'white rook':
                    castling_right += 'Q'
        if self.board[4][7] == 'black king':
            if 'k' in self.state['status_castling_right']:
                if self.board[7][7] == 'black rook':
                    castling_right += 'k'
            if 'q' in self.state['status_castling_right']:
                if self.board[0][7] == 'black rook':
                    castling_right += 'q'

        if len(castling_right) == 0:
            castling_right = '-'
        self.state['status_castling_right'] = castling_right

        move_count = int(self.state['half_moves'] / 2) + 1
        self.state['fen'] += f' {active_color} {castling_right} - 0 {move_count}'

        return self.state['fen']

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
            self.state['half_moves'] = len(move_list)
        except:
            print('ERROR: cannot get number of half moves')

        return self.state['half_moves']

    ###############################################################################################################
    # get move list
    def get_move_list(self):
        try:
            moves = self.find_element(
                By.TAG_NAME,
                'l4x'
            ).find_elements(
                By.TAG_NAME,
                'u8t'
            )
            move_list = []
            for move in moves:
                move_list.append(move.text)
            return move_list
        except:
            print('ERROR: cannot get move list')


    ###############################################################################################################
    # active color, this color has to make the next move
    def get_active_color(self):
        self.get_number_of_half_moves()
        if self.state['half_moves'] % 2 == 0:
            self.state['active_color'] = 'white'
        else:
            self.state['active_color'] = 'black'
        return self.state['active_color']

    ###############################################################################################################
    # get elapsed time in seconds from the chess clock
    def get_time_left_seconds(self):
        try:
            # we need only the time of the clock on the bottom.
            clock_bottom = self.find_element(
                By.XPATH,
                '//*[@id="main-wrap"]/main/div[1]/div[8]/div[2]'
            )
            min_sec = clock_bottom.get_attribute("textContent")
            minutes = int(min_sec[:2])
            seconds = int(min_sec[3:5])
            return minutes * 60 + seconds
        except:
            print('ERROR: cannot get time')

    ###############################################################################################################
    # get user names and rating
    def get_player_names(self):
        self.get_board_board_orientation()
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

        if self.state['board_orientation'] == 'white':
            return { "white": [bottom_user_name, bottom_user_rating], "black": [upper_user_name, upper_user_rating]}
        else:
            return { "white": [upper_user_name, upper_user_rating], "black": [bottom_user_name, bottom_user_rating]}

    ###############################################################################################################
    # ricons class: is only available if game is running
    def get_game_state(self):
        try:
            ricons = self.find_element(
                By.CLASS_NAME,
                'ricons'
            )
            self.state['game_state'] = 'running'
        except:
            self.state['game_state'] = 'finished'

        return self.state['game_state']

    ###############################################################################################################
    # get new opponent
    def get_new_opponent(self):
        try:
            new_opponent = self.find_element(
                By.XPATH,
                '//*[@id="main-wrap"]/main/div[1]/div[5]/div/a[1]'
            )
            new_opponent.click()
        except:
            print('ERROR: cannot get new opponent')

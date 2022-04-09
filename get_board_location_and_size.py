from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pyautogui

driver = webdriver.Chrome()
driver.get("https://lichess.org/tv")

board = None
absolute_board_position = { "x": 0, "y": 0 }
location_x = 0
location_y = 0
size_x = 0
size_y = 0


def board_position():
    try:
        board = driver.find_element(
            By.XPATH,
            '//*[@id="main-wrap"]/main/div[1]/div[1]/div/cg-container'
        )

        location = board.location
        location_x = location['x']
        location_y = location['y']
        size = board.size
        size_x = size['width']
        size_y = size['height']

        print(f'location_x: {location_x}, location_y: {location_y}, size_x: {size_x}, size_y: {size_y}')
    except:
        print('Board not available.')

    win_location = driver.get_window_position('current')
    print(f'window_position: {win_location}')

    canvas_x_offset = driver.execute_script("return window.screenX + (window.outerWidth - window.innerWidth) / 2 - window.scrollX;")
    canvas_y_offset = driver.execute_script("return window.screenY + (window.outerHeight - window.innerHeight) - window.scrollY;")

    print(f'canvas_x_offset: {canvas_x_offset}, canvas_y_offset: {canvas_y_offset}')
    print('-------------------------------------------------------------------------------')

    # absolute_board_position['x'] = win_location['x'] + board.location['x'] + canvas_x_offset
    # absolute_board_position['y'] = win_location['y'] + board.location['y'] + canvas_y_offset
    absolute_board_position['x'] = canvas_x_offset + location_x
    absolute_board_position['y'] = canvas_y_offset + location_y

    print('x: ' + str(absolute_board_position['x']) + ' y: ' + str(absolute_board_position['y']))

    # pyautogui.moveTo(absolute_board_position['x'], absolute_board_position['y'])
    pyautogui.moveTo(absolute_board_position['x'], absolute_board_position['y'])
    time.sleep(1)

    for x in range(3):
        x_pos = x * (size_x / 8) + size_x / 24 + absolute_board_position['x']
        for y in range(3):
            y_pos = y * (size_y / 8) + size_y / 24 + absolute_board_position['y']

            pyautogui.moveTo(x_pos, y_pos)
            print(f'x_pos: {x_pos}, y_pos: {y_pos}')
            time.sleep(0.2)

    time.sleep(5)


def get_player_names():
    bottom_user_name = driver.find_element(
        By.XPATH,
        '//*[@id="main-wrap"]/main/div[1]/div[5]/a'
    ).text

    bottom_user_rating = driver.find_element(
        By.XPATH,
        '//*[@id="main-wrap"]/main/div[1]/div[5]/rating'
    ).text

    upper_user_name = driver.find_element(
        By.XPATH,
        '//*[@id="main-wrap"]/main/div[1]/div[5]/a'
    ).text

    upper_user_rating = driver.find_element(
        By.XPATH,
        '//*[@id="main-wrap"]/main/div[1]/div[5]/rating'
    ).text
    
    print(f'User Name: {bottom_user_name}, {bottom_user_rating}')


get_player_names()



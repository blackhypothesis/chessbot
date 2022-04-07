from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import re

driver = webdriver.Chrome()
driver.get("https://lichess.org")

while True:
    try:
        clock_top = driver.find_element(
            By. XPATH,
            '//*[@id="main-wrap"]/main/div[1]/div[7]/div[2]'
        )

        clock_bottom = driver.find_element(
            By.XPATH,
            '//*[@id="main-wrap"]/main/div[1]/div[8]/div[2]'
        )
        print('clock top')
        print(clock_top.text)
        print('clock bottom')
        # print(f'__{clock_bottom.text}__')

        attribute = clock_bottom.get_attribute("textContent")
        print(attribute)
        minutes = attribute[:2]
        seconds = attribute[3:5]
        print(f'minutes: {minutes}, seconds: {seconds}')


    except:
        print('ERROR: no clock available')


    time.sleep(1)

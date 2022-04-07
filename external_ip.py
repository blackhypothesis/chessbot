from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()
driver.get("https://myexternalip.com/")

ext_ip = driver.find_element(By.ID, 'ip').text

print(f'external IP: {ext_ip}')

driver.close()
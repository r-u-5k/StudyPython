import os
import sys
import time
import pandas as pd
import numpy as np

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

import params as pa

# pd.set_option('display_width', 5000)
# pd.set_option('display_max_width', 5000)
# pd.set_option('display_max_columns', 5000)


def driversetting(DownloadPath):
    options = webdriver.ChromeOptions()
    options.add_experimental_option("prefs", {"download.default.directory": DownloadPath,
                                              "download.prompt_for_download": False,
                                              "download.directory_upgrade": True,
                                              "safebrowsing.for_trusted_sources_enabled": False,
                                              "safebrowsing.enabled": False})

    # if 1:
    #     options.add_argument("--headless")

    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-sha-usage")

    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(pa.waitseconds)

    return driver


def gen(TargetDay, Farm):  # TargetDay.Farm.Method
    driver = driversetting(pa.DownloadPath)
    driver.get(pa.HYOSUNG)
    print('Run Website')
    time.sleep(pa.waitseconds)

    driver.find_element(By.XPATH, '//*[@id="Txt_1"]').send_keys('jarasolar')
    driver.find_element(By.XPATH, '//*[@id="Txt_2"]').send_keys('abcd1234')
    driver.find_element(By.XPATH, '//*[@id="imageField"]').click()
    print('Login')
    time.sleep(pa.waitseconds)

    driver.find_element(By.XPATH, '//*[@id="form1"]/div[4]/div[1]/div/ul[2]/a[5]/li').click()
    print('Statistical Report')
    time.sleep(pa.waitseconds)

    driver.find_element(By.XPATH, '//*[@id="SrTop_cbo_plant"]/option[' + str(Farm) + ']').click()
    print('Select Farm')
    time.sleep(pa.waitseconds)

    driver.find_element(By.XPATH, '//*[@id="txt_Calendar"]').clear()
    time.sleep(pa.waitseconds)

    driver.find_element(By.XPATH, '//*[@id="txt_Calendar"]').send_keys(TargetDay)
    print('Put New Date')
    time.sleep(pa.waitseconds)

    driver.find_element(By.XPATH, '//*[@id="txt_Calendar"]').send_keys(Keys.ENTER)
    print('Close The Calendar')
    time.sleep(pa.waitseconds)

    driver.find_element(By.XPATH, '//*[@id="submitbtn"]').click()
    print('Search')
    time.sleep(pa.waitseconds)

    driver.find_element(By.XPATH, '//*[@id="exldownbtn"]').click()
    print('Download')
    time.sleep(pa.waitseconds)

    start = time.time()
    count = 0
    output = "Fail"
    while 1:
        file = os.listdir(pa.DownloadPath)
        if len(file) == 0:
            count = count + 1
            time.sleep(pa.waitseconds)
            if count == 10:
                break

        elif len(file) == 1:
            if file == 'TimeData_' + TargetDay + '.xls':
                FileName = os.path.join(pa.DownloadPath, file)
                Data = pd.read_csv(FileName)

    return []

if __name__ == "__main__":
    Farm = 1
    TargetDay = '2024-09-30'
    gen(TargetDay, Farm)

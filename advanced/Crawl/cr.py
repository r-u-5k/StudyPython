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


def gen(): # TargetDay.Farm.Method
    DownloadPath = "C:/Users/yj999/Downloads"
    driver = driversetting(DownloadPath)
    driver.get(pa.HYOSUNG)
    print('run website')

    time.sleep(pa.waitseconds)

    driver.find_element(By.XPATH, '//*[@id="Txt_1"]').send_keys('jarasolar')
    driver.find_element(By.XPATH, '//*[@id="Txt_2"]').send_keys('abcd1234')
    driver.find_element(By.XPATH, '//*[@id="imageField"]').click()
    print('login')

    return []

if __name__ == "__main__":
    gen()
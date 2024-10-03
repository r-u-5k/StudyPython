import datetime
import os
import time
import pandas as pd
import numpy as np
import psycopg2

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

import params as pa


def driversetting(DownloadPath):
    options = webdriver.ChromeOptions()
    options.add_experimental_option("prefs", {"download.default.directory": DownloadPath,
                                              "download.prompt_for_download": False,
                                              "download.directory_upgrade": True,
                                              "safebrowsing.for_trusted_sources_enabled": False,
                                              "safebrowsing.enabled": False})

    # options.add_argument("--headless")

    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-sha-usage")

    service = Service()

    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(pa.waitseconds)

    return driver


def fileremover():
    file_list = os.listdir(pa.DownloadPath)
    for f in file_list:
        if f == '.DS_Store':
            continue
        else:
            FileName = os.path.join(pa.DownloadPath, f)
            os.remove(FileName)
    return []


def GetGenData(TargetDay, Farm):  # TargetDay.Farm.Method
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

    PreNow = datetime.datetime.today()
    Today = PreNow.strftime("%Y-%m-%d")

    count = 0
    while 1:
        file = os.listdir(pa.DownloadPath)
        if len(file) == 0:
            count += 1
            time.sleep(pa.waitseconds)
            if count == 10:
                break

        elif len(file) > 0:
            TargetFile = 'HourData_' + TargetDay + '.xls'

            if TargetFile in file:
                breaker = 0
                for f in file:
                    if f == TargetFile:
                        FileName = os.path.join(pa.DownloadPath, f)
                        breaker = 1
                        break
                if breaker == 1:
                    break

    Data = getuploader(FileName, Farm)
    # fileremover()
    driver.close()

    return Data


def getuploader(FilePath, Farm):
    conn = psycopg2.connect(host=pa.host, dbname=pa.dbname, user=pa.user, password=pa.password, port=pa.port)
    cur = conn.cursor()

    Now = datetime.datetime.today() - datetime.timedelta(hours=3)

    xls_pv_html = pd.read_html(FilePath)[0]

    Result = pd.DataFrame(columns=['target', 'actual'])
    Result = Result.assign(target=xls_pv_html['시간', '시간'])
    Result = Result.assign(actual=xls_pv_html['생산량(kWh)', 'PV 발전량'])
    Result = Result.assign(actual=Result['actual'].round(0))
    Result.index = range(0, len(Result))

    RealGen = np.where(Result['target'] != 'Sum')
    Result = Result.loc[RealGen[0], :]
    Result = Result.assign(target=pd.to_datetime(Result['target'], format='%Y-%m-%d %H:%M', utc=False).dt.tz_localize(None))
    Result = Result.assign(site_id=Farm)

    for i in range(0, len(Result)):
        Target = Result.loc[i, 'target']
        SiteID = Result.loc[i, 'site_id']
        Actual = Result.loc[i, 'actual']

        if Target > Now:
            continue

        select_all_sql = f"select EXISTS(select * from solar " \
                         f"where target = TIMESTAMP '{Target}' and site_id = {SiteID})"

        cur.execute(select_all_sql)
        Exists = cur.fetchone()[0]

        if not Exists:
            print("Upload: ", Target, Actual, SiteID)
            query = f"insert into solar (target, actual, site_id) values (TIMESTAMP '{Target}', {Actual}, {SiteID})"
            cur.execute(query)

        else:
            print("Duplicated ", Target, Actual, SiteID)

    conn.commit()
    cur.close()
    conn.close()

    return Result


if __name__ == "__main__":
    Farm = 1
    TargetDay = '2024-01-31'
    GetGenData(TargetDay, Farm)

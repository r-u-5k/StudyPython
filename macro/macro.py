import os
import sys
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

import params as pa


def driver_setting(DownloadPath):
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


def macro():
    driver = driver_setting(pa.CHROME_DRIVER_PATH)
    try:
        driver.get("https://ecampus.konkuk.ac.kr/ilos/main/member/login_form.acl")
        print('Run Website')
        time.sleep(pa.waitseconds)

        # 로그인
        print("Logging in...")
        driver.find_element(By.XPATH, "//input[@id='usr_id']").send_keys(pa.userid)
        driver.find_element(By.XPATH, "//input[@id='usr_pwd']").send_keys(pa.password)
        driver.find_element(By.XPATH, "//*[@id='login_btn']").click()
        time.sleep(pa.waitseconds)
        print("Login successful")

        # 강의 페이지로 이동
        print("Navigating to lecture list...")
        WebDriverWait(driver, 30).until(  # 대기 시간 증가
            EC.element_to_be_clickable((By.XPATH, "//em[contains(text(), '온라인학습법특강 8')]"))
        ).click()
        time.sleep(pa.waitseconds)

        # 1주차 페이지로 이동
        print("Navigating to lecture contents...")
        driver.find_element(By.ID, "week-1").click()
        time.sleep(pa.waitseconds)

        # 강의 목록을 가져옴
        print("Getting lecture list...")
        weeks = driver.find_elements(By.XPATH, "//div[contains(@class, 'ibox3 wb')]")
        print("총 " + str(len(weeks)) + "주차")

        for week in weeks:
            status = week.find_element(By.CLASS_NAME, "wb-status").text.strip()

            if status == "0/1":
                week_id = week.get_attribute("id")
                print(f"클릭할 주차: {week_id}")
                driver.find_element(By.ID, week_id).click()
                time.sleep(pa.waitseconds)

                time_element = driver.find_element(By.XPATH,
                                                   "/html/body/div[3]/div[2]/div/div[2]/div[2]/div[3]/div/div/ul/li[1]/ol/li[5]/div/div/div[2]/div[3]")
                time_str = time_element.text.split("/")[2].strip()
                time_obj = datetime.strptime(time_str, "%M:%S")
                total_seconds = time_obj.minute * 60 + time_obj.second
                print(f"Lecture {week_id} duration: {total_seconds} seconds")

                driver.find_element(By.CLASS_NAME, "view").click()
                time.sleep(total_seconds)

                driver.find_element(By.ID, "close_").click()
                time.sleep(pa.waitseconds)
                print("수강 완료")

    except TimeoutException:
        print("Timeout occurred. Page might be loading slowly or elements not found.")
    except NoSuchElementException:
        print("Element not found. XPath might be incorrect or page structure changed.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        driver.quit()


if __name__ == "__main__":
    macro()

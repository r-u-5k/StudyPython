import os
import sys
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
    driver.get("https://ecampus.konkuk.ac.kr/ilos/main/member/login_form.acl")
    print('Run Website')
    time.sleep(pa.waitseconds)
    driver.find_element(By.XPATH,
                        "/html/body/div[3]/div[2]/div/div[2]/form[2]/div/div/div/fieldset/input[1]").send_keys(
        pa.userid)
    driver.find_element(By.XPATH,
                        "/html/body/div[3]/div[2]/div/div[2]/form[2]/div/div/div/fieldset/input[2]").send_keys(
        pa.password)
    driver.find_element(By.XPATH, "/html/body/div[3]/div[2]/div/div[2]/form[2]/div/div/div/div[1]").click()
    time.sleep(pa.waitseconds)

    # 강의 목록 페이지로 이동
    print("Navigating to lecture list...")
    WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "/html/body/div[3]/div[2]/div/div/div[2]/div[2]/ol/li[18]/em"))
    ).click()
    time.sleep(pa.waitseconds)

    # 강의 컨텐츠 페이지로 이동
    print("Navigating to lecture contents...")
    WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "/html/body/div[3]/div[2]/div/div[2]/div[2]/div[2]/div[2]/div/div[1]"))
    ).click()
    time.sleep(pa.waitseconds)

    # 강의 목록을 가져옵니다
    print("Getting lecture list...")
    lectures = WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'lecture_container')]"))
    )
    print(f"Found {len(lectures)} lectures")
    for i, lecture in enumerate(lectures, start=1):
        try:
            print(f"Checking lecture {i}...")
            progress_text = lecture.find_element(By.XPATH, ".//div[@class='progress-text']").text
            print(f"Lecture {i} progress: {progress_text}")
            if progress_text == "0/1":
                print(f"Starting lecture {i}")
                lecture.click()
                time.sleep(pa.waitseconds)
                time_element = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'video_time')]"))
                )
                time_str = time_element.text.split("/")[1].strip()
                time_obj = datetime.strptime(time_str, "%M:%S")
                total_seconds = time_obj.minute * 60 + time_obj.second
                print(f"Lecture {i} duration: {total_seconds} seconds")
                play_button = WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'vjs-play-control')]"))
                )
                play_button.click()
                print(f"Watching lecture {i} for {total_seconds} seconds")
                time.sleep(total_seconds)
                back_button = WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[contains(@class, 'learning_content_close')]"))
                )
                back_button.click()
                time.sleep(pa.waitseconds)
                print(f"Finished lecture {i}")
            else:
                print(f"Skipping lecture {i} (already watched)")
        except Exception as e:
            print(f"Error processing lecture {i}: {str(e)}")
            continue


if __name__ == "__main__":
    macro()

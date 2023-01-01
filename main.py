import re
import logging
import time
from collections import Counter
from pushbullet import Pushbullet

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime, timedelta
import json

options = webdriver.ChromeOptions()
options.add_argument("disable-dev-shm-usage")
data_file = open('data.json')
data = json.load(data_file)
access_token = data['token']
badi_link = data['badi_link']
idealista_link = data['idealista_link']
pb = Pushbullet(access_token)
logging.basicConfig(level=logging.INFO)

room_list = []


# def scrape_idealista():
#     driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
#     wait = WebDriverWait(driver, 6)
#     driver.get(idealista_link)
#     time.sleep(5)
#     idealista_page = driver.current_url
#
#     room_list = driver.find_elements("xpath", ("//article[starts-with(@class, 'item item-multimedia-container')]"))
#     for element in room_list:
#         room_div = element.find_element(By.CLASS_NAME, 'item-info-container')
#         room_link = room_div.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
#         room_link_cleaned = re.sub(r'\?.*', '', room_link)
#         logging.info(room_link_cleaned)
#         check_and_add(room_link_cleaned, room_list)
#     driver.close()
#     logging.info("Scraped Idealista")

rooms = []
def scrape_badi():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 6)
    driver.get(badi_link)
    time.sleep(5)
    badi_page = driver.current_url
    room_links = []


    room_list = driver.find_elements("xpath", ("//div[starts-with(@id, 'list-room-card')]"))
    for element in room_list:
        room_link = element.find_element(By.CSS_SELECTOR, 'a[data-qa="room-card-link"]').get_attribute('href')
        room_link_cleaned = re.sub(r'\?.*', '', room_link)
        logging.info(room_link_cleaned)
        room_links.append(room_link_cleaned)

    for room in room_links:
        check_if_recent(driver, room, rooms)

    driver.close()
    logging.info("Checked Badi")


def check_if_recent(driver, link, database):
    driver.get(link)
    time_published = driver.find_element("xpath", (
        "/html/body/div[2]/div[2]/div[2]/div/div[1]/div/div[1]/div/div/div[1]/div/section/div[2]/div/div/div/div[2]/div/div[4]/p/time")).get_attribute(
        'datetime')

    formatted_time = datetime.strptime(time_published, "%Y-%m-%d %H:%M")

    if formatted_time > datetime.now() - timedelta(minutes=63):
        if link not in database:
            database.append(link)
            time = datetime.now().strftime("%H:%M:%S")
            pb.push_link(f"New flat found at {time}", link)
            logging.info(f'New flat found at {time}: {link}')

while True:
    scrape_badi()
    time.sleep(60)

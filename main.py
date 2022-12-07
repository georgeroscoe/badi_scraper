import re
import logging
import time
from pushbullet import Pushbullet

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import json

options = webdriver.ChromeOptions()
options.add_argument("disable-dev-shm-usage")


data_file = open('data.json')
data = json.load(data_file)
access_token = data['token']
badi_link = data['badi_link']
pb = Pushbullet(access_token)
logging.basicConfig(level=logging.INFO)
badi_list = []


def scrape_badi():
    # driver = webdriver.Chrome(service=Service(os.environ.get("CHROMEDRIVER_PATH")), options=options)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    wait = WebDriverWait(driver, 10)
    driver.get(badi_link)
    badi_page = driver.current_url

    room_list = driver.find_elements("xpath", "//div[@id]")
    regex_pattern = re.compile(r"^list-room-card-*")
    for element in room_list:
        logging.info(regex_pattern.search(element.get_attribute("id")))
        if regex_pattern.search(element.get_attribute("id")):
            room_link = element.find_element(By.CSS_SELECTOR, 'a[data-qa="room-card-link"]').get_attribute('href')
            room_link_cleaned = re.sub(r'\?.*', '', room_link)
            check_and_add(room_link_cleaned, badi_list)
    driver.close()
    logging.info("Checked Badi")


def check_and_add(item, database):
    if item not in database:
        database.append(item)
        time = datetime.now().strftime("%H:%M:%S")
        pb.push_link(f"New flat found at {time}", item)
        logging.info(f'New flat found at {time}: {item}')


# def check_new_elements(prev_output, curr_output):
#     # Count the number of occurrences of each element in the outputs
#     prev_count = Counter(prev_output)
#     curr_count = Counter(curr_output)
#
#     new_element_count = 0
#
#     # Compare the counts of the elements in the previous and current outputs
#     # If there are any elements in the current output that were not present in the previous output, send an email notification
#     for element in curr_count:
#         if element not in prev_count:
#             send_notification(element)
#             new_element_count += 1
#     if new_element_count == 0:
#         time = datetime.now().strftime("%H:%M:%S")
#         logging.info(f"No new flats found at {time}")
#     else:
#         logging.info("Notification sent")
#         logging.info(curr_count)
#         logging.info(prev_count)
#
#
# def send_notification(element):
#     time = datetime.now().strftime("%H:%M:%S")
#     # pb.push_link(f"New flat found at {time}", element)


while True:
    scrape_badi()
    time.sleep(60)

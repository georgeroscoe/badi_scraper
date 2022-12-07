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
from datetime import datetime
import json

options = webdriver.ChromeOptions()
options.add_argument("start-maximized")
options.add_experimental_option('excludeSwitches', ['enable-logging'])
data_file = open('data.json')
data = json.load(data_file)
access_token = data['token']
badi_link = data['link']
pb = Pushbullet(access_token)
logging.basicConfig(level=logging.INFO)




def scrape_badi():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 6)
    driver.get(badi_link)
    badi_page = driver.current_url

    room_list = driver.find_elements("xpath", "//div[@id]")
    regex_pattern = re.compile(r"^list-room-card-*")
    matching_elements = []
    for element in room_list:
        if regex_pattern.search(element.get_attribute("id")):
            room_link = element.find_element(By.CSS_SELECTOR, 'a[data-qa="room-card-link"]').get_attribute('href')
            matching_elements.append(room_link)
    driver.close()
    logging.info("Scraped Badi")
    return matching_elements


def check_new_elements(prev_output, curr_output):
    # Count the number of occurrences of each element in the outputs
    prev_count = Counter(prev_output)
    curr_count = Counter(curr_output)

    new_element_count = 0

    # Compare the counts of the elements in the previous and current outputs
    # If there are any elements in the current output that were not present in the previous output, send an email notification
    for element in curr_count:
        if element not in prev_count or curr_count[element] > prev_count[element]:
            send_notification(element)
            new_element_count += 1
    if new_element_count == 0:
        time = datetime.now().strftime("%H:%M:%S")
        logging.info(f"No new flats found at {time}")


def send_notification(element):
    time = datetime.now().strftime("%H:%M:%S")
    pb.push_link(f"New flat found at {time}", element)
    logging.info("Notification sent")


previous_output = None

while True:
    current_output = scrape_badi()
    check_new_elements(previous_output, current_output)
    previous_output = current_output
    time.sleep(60)
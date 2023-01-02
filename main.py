import re
import logging
import time

from pushbullet import Pushbullet
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime, timedelta
import json

# Set up logger
logging.basicConfig(level=logging.INFO)


# Read data from JSON file
with open('data.json', 'r') as data_file:
    data = json.load(data_file)

access_token = data['token']
badi_link = data['badi_link']
# idealista_link = data['idealista_link']

# Initialize Pushbullet client
pb = Pushbullet(access_token)

# Set up Chrome options
options = webdriver.ChromeOptions()
options.add_argument("disable-dev-shm-usage")

# Create a global instance of the Chrome driver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Wait object for synchronizing tests
wait = WebDriverWait(driver, 6)

rooms = []


def scrape_badi():
    """
    Scrape the Badi webpage for room listings.
    """
    driver.get(badi_link)
    badi_page = driver.current_url
    room_links = []
    wait
    logging.info("Reached listing page")

    # Find all room listings on the page
    room_list_elements = driver.find_elements("xpath", ("//div[starts-with(@id, 'list-room-card')]"))
    for element in room_list_elements:
        room_link_element = element.find_element(By.CSS_SELECTOR, 'a[data-qa="room-card-link"]')
        room_link = room_link_element.get_attribute('href')
        room_link_cleaned = re.sub(r'\?.*', '', room_link)
        logging.info(room_link_cleaned)
        room_links.append(room_link_cleaned)

    for room_link in room_links:
        check_if_recent(driver, room_link, rooms)

    logging.info("Checked Badi")
    driver.close()

def send_notification(link):
    """
    Send a notification through Pushbullet with the given link.
    """
    current_time = datetime.now().strftime("%H:%M:%S")
    pb.push_link(f"New flat found at {current_time}", link)
    logging.info(f'New flat found at {current_time}: {link}')

def is_recent(time_string):
    """
    Check if a room listing is recent based on the given time string.
    """
    formatted_date = datetime.strptime(time_string, "%Y-%m-%d %H:%M")
    return formatted_date > datetime.now() - timedelta(minutes=63)

def check_if_recent(driver, link, database):
    """
    Check if a room listing is recent and notify the user if it is.
    """
    driver.get(link)
    time_element = wait.until(
        lambda d: d.find_element("xpath", (
        "/html/body/div[2]/div[2]/div[2]/div/div[1]/div/div[1]/div/div/div[1]/div/section/div[2]/div/div/div/div[2]/div/div[4]/p/time"))
    )
    time_string = time_element.get_attribute('datetime')

    if is_recent(time_string):
        if link not in database:
            database.append(link)
            send_notification(link)


while True:
    scrape_badi()
    time.sleep(60)
